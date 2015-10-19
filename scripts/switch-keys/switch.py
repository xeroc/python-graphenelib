#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
from grapheneapi import GrapheneWebsocket, GrapheneWebsocketProtocol
import time
import config
import subprocess
from time import gmtime, strftime


rpc = GrapheneWebsocket("localhost", 8092, "", "")



def closeScreens():
    print("closing wallet")
    time.sleep(15) #adding this to give some time to ctrl-c before --resync if desired
    subprocess.call(["screen","-S","wallet","-p","0","-X","quit"])
    time.sleep(2)
    print("closing witness")
    subprocess.call(["screen","-S","witness","-p","0","-X","quit"])
    time.sleep(2)
    subprocess.call(["pkill","witness_node"])
    time.sleep(2)

def openScreens():
    print("opening witness")
    subprocess.call(["screen","-dmS","witness",config.path_to_witness_node,"-d",config.path_to_data_dir,"--replay-blockchain"])
    print("waiting..." + "replay = " + str(replay) + "                     crash = " + str(crash))
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
    print(str(block) + "     " + str(age) + "     " + str(participation) + "      replay = " + str(replay) + "      crash = " + str(crash))

def watch(tries):
    if float(info()) < 50:
        if tries > 2:
            closeScreens()
            resync()
            print("unlocking wallet")
            rpc.unlock(config.wallet_password)
            print("wallet unlocked")
            time.sleep(30)
            tries = 0
            return tries

        else:
            closeScreens()
            openScreens()
            print("unlocking wallet")
            rpc.unlock(config.wallet_password)
            print("wallet unlocked")
            time.sleep(30)
            tries += 1
            return tries
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

### testing running feed schedule through script
def checkTime():
    minute = strftime("%M", gmtime())
    minute = int(minute)
    if minute % 60 == config.feed_script_time:
        subprocess.call(["screen","-S","feed","-p","0","-X","quit"])
        subprocess.call(["screen","-dmS","feed","python3",config.path_to_feed])
        time.sleep(60)



recentmissed = 0
emergency = False
replay = 3
crash = 0
lastHour = 0
closeScreens()
openScreens()
print("unlocking wallet")
rpc.unlock(config.wallet_password)

missed = getMissed(config.witnessname)
witness = rpc.get_witness(config.witnessname)
lastblock = witness["last_confirmed_block_num"]

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
#            lastHour = checkTime(lastHour)
            waitAndNotify()
            tries = replay
            replay = watch(tries)
### if you are having issue try commenting out the try line (126) and everything below the except line to prevent auto restart
    except:
        try:
            if crash > 2:
                crash = 0
                closeScreens()
                resync()
                print("unlocking wallet")
                rpc.unlock(config.wallet_password)
                print("wallet unlocked")
            else:
                crash += 1
                print("error.  restarting.")
                closeScreens()
                openScreens()
                print("unlocking wallet")
                rpc.unlock(config.wallet_password)
                print("wallet unlocked")
        except:
            try:
                if crash > 2:
                    crash = 0
                    closeScreen()
                    resync()
                    print("unlocking wallet")
                    rpc.unlock(config.wallet_password)
                else:
                    crash += 1
                    print("error... restarting")
                    closeScreens()
                    openScreens()
                    print("unlocking wallet")
                    rpc.unlock(config.wallet_password)
            except:
                try:
                    if crash > 2:
                        crash = 0
                        closeScreens()
                        resync()
                        print("unlocking wallet")
                        rpc.unlock(config.wallet_password)
                    else:
                        crash += 1
                        print("error.  restarting.")
                        closeScreens()
                        openScreens()
                        print("unlocking wallet")
                        rpc.unlock(config.wallet_password)
                except:
                    crash = 0
                    closeScreens()
                    resync()
                    print("unlocking wallet")
                    rpc.unlock(config.wallet_password)




