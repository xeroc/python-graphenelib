#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
from grapheneapi import GrapheneWebsocket, GrapheneWebsocketProtocol
import time
import config
import subprocess
from time import gmtime, strftime
from producer1 import producer1


from producer2 import producer2




rpc = GrapheneWebsocket("localhost", 8092, "", "")

def unlockWallet():
    if config.feed_script_active == True or config.switching_active == True:
        print("unlocking wallet")
        rpc.unlock(config.wallet_password)
        time.sleep(11)

def closeScreens():
    print("closing wallet")
    subprocess.call(["screen","-S","local-wallet","-p","0","-X","quit"])
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
    print("checking if witness_node is ready for communication yet")
    result = None
    while result == None:
        try:
            print("waiting ...")
            subprocess.call(["screen","-dmS","local-wallet",config.path_to_cli_wallet,"-H",config.rpc_port,"-w",config.path_to_wallet_json])
            time.sleep(1)
            result = rpc.info()
        except:
            time.sleep(10)
            pass

def info():
    info = rpc.info()
    part = info["participation"]
    block = info["head_block_num"]
    age = info["head_block_age"]
    return part

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
            unlockWallet()
            tries = 0
            return tries
        else:
            closeScreens()
            openScreens()
            unlockWallet()
            tries += 1
            return tries
    else:
        return 0

def resync():
    print("--replay failed.  --resync underway")
    print("opening witness with --resync-blockchain.  Please CTRL C now if you do not want to wipe your data_dir")
    time.sleep(15)
    subprocess.call(["screen","-dmS","witness",config.path_to_witness_node,"-d",config.path_to_data_dir,"--resync-blockchain"])
    print("checking if witness_node is ready for communication yet")
    result = None
    while result == None:
        try:
            print("waiting ...")
            subprocess.call(["screen","-dmS","local-wallet",config.path_to_cli_wallet,"-H",config.rpc_port,"-w",config.path_to_wallet_json])
            time.sleep(1)
            result = rpc.info()
        except:
            time.sleep(10)
            pass

### testing running feed schedule through script
def checkTime():
    if config.feed_script_active == True:
        if feed == True:
            minute = strftime("%M", gmtime())
            minute = int(minute)
            trigger = config.feed_script_trigger
            interval = config.feed_script_interval
            if minute % interval == trigger:
                subprocess.call(["screen","-S","feed","-p","0","-X","quit"])
                subprocess.call(["screen","-dmS","feed","python3",config.path_to_feed_script])
                time.sleep(60)
                return False
            else:
                return True
        else:
            minute = strftime("%M", gmtime())
            minute = int(minute)
            trigger = config.feed_script_trigger
            interval = config.feed_script_interval
            if minute % interval == trigger:
                return False
            else:
                return True


def compareSigningKeys():
    if producer1.getSigningKey() == producer2.getSigningKey():
        print("node1 signing key= "+producer1.getSigningKey()+"       node1 witness participation = " + str(producer1.info()))
        print("node2 signing key= "+producer2.getSigningKey()+"       node2 witness participation = " + str(producer2.info()))
        return True
    else:
        print("ERROR....ERROR....ERROR....ERROR....ERROR")
        print("signing keys are different.  You have been forked")
        return False

def setRemoteKey(num):
    if num == 0:
        return
    elif num == 1:
        signingKey = producer1.getSigningKey()
        producer2.setSigningKey(signingKey)
    elif num == 2:
        signingKey = producer2.getSigningKey()
        producer1.setSigningKey(signingKey)

def comparePart():
    if producer1.info() == producer2.info():
        return 0
    elif producer1.info() > producer2.info():
        return 1
    elif producer2.info() > producer1.info():
        return 2

def getMissed(witnessname):
    witness = rpc.get_witness(witnessname)
    missed = witness["total_missed"]
    return missed

# add check for age of head block, and last block vs head block
def switch(witnessname, publickeys, missed):
    if config.switching_active == True:
        blockAge = rpc.info()
        blockAge = blockAge["head_block_age"]
        blockAgeInt = int(blockAge.split()[0])
        blockAgeString = str(blockAge.split()[1])
        if blockAgeString == "second" or blockAgeString == "seconds":
            if blockAgeInt < 60:
                keynumber = (missed//config.strictness) % len(publickeys)
                key = publickeys[keynumber]
                rpc.update_witness(witnessname, "", key, "true")
                print("updated signing key to " + key)

feed = True
replay = 0
crash = 0
producer1.closeProducer()
producer2.closeProducer()
producer1.openProducer()
producer2.openProducer()
time.sleep(2)
#compareSigningKeys()
closeScreens()
openScreens()
time.sleep(2)
unlockWallet()
time.sleep(2)
witness = rpc.get_witness(config.witnessname)
lastblock = witness["last_confirmed_block_num"]
missed = getMissed(config.witnessname)

while True:
#    try:
        witness = rpc.get_witness(config.witnessname)
        if lastblock < witness["last_confirmed_block_num"]:
            lastblock = witness["last_confirmed_block_num"]
            print(config.witnessname + " generated block num " + str(lastblock))
        elif missed <= getMissed(config.witnessname) - config.strictness:
            missed = getMissed(config.witnessname)
            switch(config.witnessname, config.publickeys, missed)
            print(config.witnessname + " missed a block.  total missed = " + str(missed))
            lastblock = witness["last_confirmed_block_num"]
        else:
            try:
                if compareSigningKeys() == False:
                    choice = comparePart()
                    setRemoteKey(choice)
            except:
                try:
                    part1 = producer1.info()
                    print(part1)
                except:
                    print("producer1 no workie")
                    producer1.closeProducer()
                    producer1.openProducer()
                try:
                    part2 = producer2.info()
                    print(part2)
                except:
                    producer2.closeProducer()
                    producer2.openProducer()

            checkTime()
            waitAndNotify()
            tries = replay
            replay = watch(tries)
### For debugging comment out try statement directly below while True line, and uncomment line line below this line and last line of script
'''
    except:
        try:
            if crash > 2:
                crash = 0
                closeScreens()
                resync()
                unlockWallet()
            else:
                crash += 1
                print("error.  restarting.")
                closeScreens()
                openScreens()
                unlockWallet()
        except:
            try:
                if crash > 2:
                    crash = 0
                    closeScreen()
                    resync()
                    unlockWallet()
                else:
                    crash += 1
                    print("error... restarting")
                    closeScreens()
                    openScreens()
                    unlockWallet()
            except:
                try:
                    if crash > 2:
                        crash = 0
                        closeScreens()
                        resync()
                        unlockWallet()
                    else:
                        crash += 1
                        print("error.  restarting.")
                        closeScreens()
                        openScreens()
                        unlockWallet()
                except:
                    crash = 0
                    closeScreens()
                    resync()
                    unlockWallet()
'''







