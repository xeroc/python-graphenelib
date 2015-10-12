#!/usr/bin/env python
# -*- coding: utf-8 -*-

### You must have a config.py with the following parameters.
### witnessname = <the name of your witness>
### publickeys = <tuple of public keys as strings> i.e. ("GPH57pBVHtJzfsZZ117e5dBfaMTJxbfzfZQRFFMVuompRQAidAEwK", "GPH75xxKG4ZeztPpnhmFch99smunUWMvDy9mB6Le497vpAA3XUXaD") must have at least 2
### strictness = <the number of blocks missed before a new public key is switched to> must be set to 1 or higher.
### emergencykeys = <tuple of emergency public keys as strings>  If no emergency nodes are used set emergency keys = 0.  If keys are used, must have at least two entries.  Can use same key twice if only running single emergency node
### If all public keys fail to produce blocks after two rotations, then emergencykeys will be used.
### If all emergency keys fail to produce blocks after two rotations, then attempt will be made to switch back to primary keys
### If emegergency keys produce blocks attempt will still be made to switch back to primary keys after 30ish minutes


import sys
import json
from grapheneapi import GrapheneWebsocket, GrapheneWebsocketProtocol
import time
import config

rpc = GrapheneWebsocket("localhost", 8092, "", "")

### returns total missed blocks from witnessname
def getmissed(witnessname):
    witness = rpc.get_witness(witnessname)
    missed = witness["total_missed"]
    return missed

### work on cleaning up these preliminary variables
missed = getmissed(config.witnessname)
recentmissed = 0
witness = rpc.get_witness(config.witnessname)
lastblock = witness["last_confirmed_block_num"]
emergency = False

### switches to next public key after config.strictness missed blocks
def switch(witnessname, publickeys, missed):
    keynumber = (missed//config.strictness) % len(publickeys)
    key = publickeys[keynumber]
    rpc.update_witness(witnessname, "", key, "true")
    print("updated signing key to " + key)

### break some of this out into separate functions.
while True:
    witness = rpc.get_witness(config.witnessname)
    if lastblock < witness["last_confirmed_block_num"]:
        lastblock = witness["last_confirmed_block_num"]
        print(config.witnessname + " generated block num " + str(lastblock))
        recentmissed = 0
    elif config.emergencykeys != 0:
        if emergency == True:
            witness = rpc.get_witness(config.witnessname)
            if missed <= getmissed(config.witnessname) - config.strictness:
                missed = getmissed(config.witnessname)
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
                time.sleep(3)
                info = rpc.info()
                block = info["head_block_num"]
                age = info["head_block_age"]
                participation = info["participation"]
                print(str(block) + "     " + str(age) + "     " + str(participation))
        elif recentmissed > len(config.publickeys) * 2:
            emergency = True
            missed = getmissed(config.witnessname)
            switch(config.witnessname, config.emergencykeys, missed)
            recentmissed = 0
            lastblock = witness["last_confirmed_block_num"]
            print("all primary nodes down. switching to emergency nodes")
            emergencyblock = block
        elif missed <= getmissed(config.witnessname) - config.strictness:
            missed = getmissed(config.witnessname)
            switch(config.witnessname, config.publickeys, missed)
            recentmissed +=1
            print(config.witnessname + " missed a block.  total missed = " + str(missed) + " recent missed = " + str(recentmissed))
            lastblock = witness["last_confirmed_block_num"]
        else:
            time.sleep(3)
            info = rpc.info()
            block = info["head_block_num"]
            age = info["head_block_age"]
            participation = info["participation"]
            print(str(block) + "     " + str(age) + "     " + str(participation))

    elif missed <= getmissed(config.witnessname) - config.strictness:
        missed = getmissed(config.witnessname)
        switch(config.witnessname, config.publickeys, missed)
        recentmissed +=1
        print(config.witnessname + " missed a block.  total missed = " + str(missed) + " recent missed = " + str(recentmissed))
        lastblock = witness["last_confirmed_block_num"]
    else:
        time.sleep(3)
        info = rpc.info()
        block = info["head_block_num"]
        age = info["head_block_age"]
        participation = info["participation"]
        print(str(block) + "     " + str(age) + "     " + str(participation))

