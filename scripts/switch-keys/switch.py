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
    if config.feed_script_active == True:
        print("unlocking wallet")
        rpc.unlock(config.wallet_password)
        time.sleep(10)

def closeScreens():
    print("closing wallet")
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
    print("waiting...")
    time.sleep(600)
    print("opening wallet")
    subprocess.call(["screen","-dmS","wallet",config.path_to_cli_wallet,"-H",config.rpc_port,"-w",config.path_to_wallet_json])
    print("waiting...")
    time.sleep(10)

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
        return True
    else:
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
    elif producer1.info() > producer1.info():
        return 2

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

feed = True
replay = 0
crash = 0
closeScreens()
openScreens()
unlockWallet()
witness = rpc.get_witness(config.witnessname)
lastblock = witness["last_confirmed_block_num"]
missed = getMissed(config.witnessname)
try:
    producer1.closeProducer()
    producer1.openProducer()
except:
    print ("producer1 unable to open")
try:
    producer2.closeProducer()
    producer2.openProducer()
except:
    print ("producer2 unable to open")

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
                if compareSigningKeys == False:
                    setRemoteKey(comparePart())
            except:
                try:
                    print("producer1 witness participation = " + producer1.info())
                except:
                    print("producer1 no workie")
                    producer1.closeProducer()
                    producer1.openProducer()
                    print("producer1 witness participation = " + producer1.info())
                try:
                    print("producer2 witness participation = " + producer2.info())
                except:
                    producer2.closeProducer()
                    producer2.openProducer()
                    print("producer2 witness participation = " + producer2.info())


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







