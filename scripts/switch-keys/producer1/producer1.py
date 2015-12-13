import sys
import json
from grapheneapi import GrapheneWebsocket, GrapheneWebsocketProtocol
import time
import subprocess

path_to_cli_wallet = "/home/user/src/bitshares-2/programs/cli_wallet/cli_wallet"

wallet_password = "puppiesRkewl"

remote_ws = "ws://192.241.239.195:8090"

private_active_key = "5JVVeSuCHviTJSY3LKyQJ4t4s4coiVN7qw3M4XzWYQgZ2XzaJu1"

witnessname = "test.dele-puppy"

producer_number = 1

rpc_port = "8093"

wallet_name = "wallet1.json"



rpc = GrapheneWebsocket("ws://localhost:%d"%rpc_port, "", "")
local_port = "127.0.0.1:" + rpc_port


def tryProducer():
    attempt = 0
    while attempt < 5:
        attempt +=1
        print("attempt #" + attempt + " to reconnect to " + wallet_name)
        subprocess.call(["screen","-dmS",wallet_name,path_to_cli_wallet,"-H",local_port,"-s",remote_ws,"--chain-id","16362d305df19018476052eed629bb4052903c7655a586a0e0cfbdb0eaf1bfd8"]) ### uncomment this line if running on testnet
#        subprocess.call(["screen","-dmS",wallet_name,path_to_cli_wallet,"-H",local_port,"-s",remote_ws,"]) ### comment this line out if running on testnet
        time.sleep(1)




def openProducer():
    print("opening " + wallet_name)
    attempt = 0
    result = None
    while result == None:
        if attempt < 4:

            try:
                print("waiting ...")
                subprocess.call(["screen","-dmS",wallet_name,path_to_cli_wallet,"-H",local_port,"-s",remote_ws,"-w","producer1/" + wallet_name,"--chain-id","16362d305df19018476052eed629bb4052903c7655a586a0e0cfbdb0eaf1bfd8"]) ### uncomment this line if running on testnet
#                subprocess.call(["screen","-dmS",wallet_name,path_to_cli_wallet,"-H",local_port,"-s",remote_ws,"-w","producer1/" + wallet_name"]) ### comment this line out if running on testnet
                time.sleep(1)
                checkIfNew()
                unlockWallet()
                result = rpc.info()
            except:
                time.sleep(10)
                attempt += 1
                pass
        else:
            break



def closeProducer():
    subprocess.call(["screen","-S",wallet_name,"-p","0","-X","quit"])

def unlockWallet():
    print("unlocking " + wallet_name)
    while rpc.is_locked() == True:
        try:
            rpc.unlock(wallet_password)
        except:
            time.sleep(10)
            pass

def checkIfNew():
    try:
        if rpc.is_new() == True:
            print("checking if new")
            setPassword()
            unlockWallet()
            importActiveKey()
            saveWallet()
        else:
            pass
    except:
        pass

def setPassword():
    print("setting password")
    rpc.set_password(wallet_password)

def importActiveKey():
    print("importing key")
    rpc.import_key(witnessname, private_active_key)

def getSigningKey():
    witness = rpc.get_witness(witnessname)
    signingKey = witness["signing_key"]
    return signingKey

def setSigningKey(signingKey):
    rpc.update_witness(witnessname,"",signingKey,"true")


def saveWallet():
    print("saving wallet")
    rpc.save_wallet_file("producer1/" + wallet_name)

def info():
    info = rpc.info()
    part = info["participation"]
    part = float(part)
    return part
