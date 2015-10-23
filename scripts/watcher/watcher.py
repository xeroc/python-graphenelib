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

def unlockWallet():
    if config.feed_script_active = True:
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
    minute = strftime("%M", gmtime())
    minute = int(minute)
    time = config.feed_script_time
    if minute % 60 == time:
        subprocess.call(["screen","-S","feed","-p","0","-X","quit"])
        subprocess.call(["screen","-dmS","feed","python3",config.path_to_feed_script])
        time.sleep(60)


replay = 0
crash = 0
closeScreens()
openScreens()
unlockWallet()



while True:
    try:
            checkTime()
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




