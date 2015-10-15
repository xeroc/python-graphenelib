#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
from grapheneapi import GrapheneWebsocket, GrapheneWebsocketProtocol
import time
import config
import subprocess


rpc = GrapheneWebsocket("localhost", 8092, "", "")



def closeScreens():
    print("closing wallet")
    subprocess.call(["screen","-S","wallet","-p","0","-X","quit"])
    print("closing witness")
    subprocess.call(["screen","-S","witness","-p","0","-X","quit"])
    subprocess.call(["pkill","witness_node"])

def openScreens():
    print("opening witness")
    subprocess.call(["screen","-dmS","witness",config.path_to_witness_node,"-d",config.path_to_data_dir,"--replay-blockchain"])
    print("waiting...")
    time.sleep(180)
    print("opening wallet")
    subprocess.call(["screen","-dmS","wallet",config.path_to_cli_wallet,"-H",config.rpc_port,"-w",config.path_to_wallet_json])
    print("waiting...")
    time.sleep(10)

def info():
    info = rpc.info()
    part = info["participation"]
    block = info["head_block_num"]
    age = info["head_block_age"]
    return part

def getMissed(witnessname):
    witness = rpc.get_witness(witnessname)
    missed = witness["total_missed"]
    return missed

# add check for age of head block, and last block vs head block
def switch(witnessname, publickeys, missed):
    keynumber = (missed//config.strictness) % len(publickeys)
    key = publickeys[keynumber]
    rpc.update_witness(witnessname, "", key, "true")
    print("updated signing key to " + key)

def waitAndNotify():
    time.sleep(3)
    info = rpc.info()
    block = info["head_block_num"]
    age = info["head_block_age"]
    participation = info["participation"]
    print(str(block) + "     " + str(age) + "     " + str(participation))

def watch(num):
    if num > 2:
        closeScreens()
        resysnc()
        rpc.unlock(config.wallet_password)
        time.sleep(30)
        return 0
    elif float(info()) < 50:
        closeScreens()
        openScreens()
        rpc.unlock(config.wallet_password)
        time.sleep(30)
        num =+ 1
        return num
    else:
        return 0

def resync():
    print("--replay failed.  --resync underway")
    print("opening witness")
    subprocess.call(["screen","-dmS","witness",config.path_to_witness_node,"-d",config.path_to_data_dir,"--resync-blockchain"])
    print("waiting...")
    time.sleep(300)
    print("opening wallet")
    subprocess.call(["screen","-dmS","wallet",config.path_to_cli_wallet,"-H",config.rpc_port,"-w",config.path_to_wallet_json])
    print("waiting...")
    time.sleep(10)


closeScreens()
openScreens()
print("unlocking wallet")
rpc.unlock(config.wallet_password)

missed = getMissed(config.witnessname)
recentmissed = 0
witness = rpc.get_witness(config.witnessname)
lastblock = witness["last_confirmed_block_num"]
emergency = False
replay = 0

while True:
    try:
        witness = rpc.get_witness(config.witnessname)
        if lastblock < witness["last_confirmed_block_num"]:
            lastblock = witness["last_confirmed_block_num"]
            print(config.witnessname + " generated block num " + str(lastblock))
            recentmissed = 0
        elif config.emergencykeys != 0:
            if emergency == True:
                witness = rpc.get_witness(config.witnessname)
                if missed <= getMissed(config.witnessname) - config.strictness:
                    missed = getMissed(config.witnessname)
                    switch(config.witnessname, config.emergencykeys, missed)
                    recentmissed +=1
                    lastblock = witness["last_confirmed_block_num"]
                    print("EMERGENCY!!! total missed = " + str(missed) + " recent missed = " + str(recentmissed))
                elif emergencyblock < block - 600:
                    emergency = False
                    switch(config.witnessname, config.publickeys, missed)
                    recentmissed = 0
                    print("attempting to switch back to primary nodes")
                elif recentmissed == len(config.emergencykeys) * 2:
                    emergency = False
                    switch(config.witnessname, config.publickeys, missed)
                    recentmissed = 0
                    print("attempting to switch back to primary nodes")
                else:
                    waitAndNotify()
            elif recentmissed > len(config.publickeys) * 2:
                emergency = True
                missed = getMissed(config.witnessname)
                switch(config.witnessname, config.emergencykeys, missed)
                recentmissed = 0
                lastblock = witness["last_confirmed_block_num"]
                print("all primary nodes down. switching to emergency nodes")
                emergencyblock = block
            elif missed <= getMissed(config.witnessname) - config.strictness:
                missed = getMissed(config.witnessname)
                switch(config.witnessname, config.publickeys, missed)
                recentmissed +=1
                print(config.witnessname + " missed a block.  total missed = " + str(missed) + " recent missed = " + str(recentmissed))
                lastblock = witness["last_confirmed_block_num"]
            else:
                waitAndNotify()
        elif missed <= getMissed(config.witnessname) - config.strictness:
            missed = getMissed(config.witnessname)
            switch(config.witnessname, config.publickeys, missed)
            recentmissed +=1
            print(config.witnessname + " missed a block.  total missed = " + str(missed) + " recent missed = " + str(recentmissed))
            lastblock = witness["last_confirmed_block_num"]
        else:
            waitAndNotify()
            replay = watch(replay)
    except:
        if crash > 2:
            crash = watch(crash)
        else:
            print("error.  restarting.")
            closeScreens()
            openScreens()
            crash =+ 1



