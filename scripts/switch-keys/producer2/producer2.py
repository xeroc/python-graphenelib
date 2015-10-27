import sys
import json
from grapheneapi import GrapheneWebsocket, GrapheneWebsocketProtocol
import time
import subprocess

path_to_cli_wallet = "/home/user/src/bitshares-2/programs/cli_wallet/cli_wallet"

wallet_password = "puppiesRkewl"

remote_ws = "ws://192.241.239.195:8090"

private_active_key = "5JxBDZG3DvRXnUDPeSjRxZWpMWiZkZvMh5sRRDKJZUwRdgMP7vf"

witnessname = "dele-puppy"

producer_number = 1

rpc_port = "8093"

wallet_name = "wallet1"



rpc = GrapheneWebsocket("localhost", rpc_port, "", "")
local_port = "127.0.0.1:" + rpc_port

def openProducer():
    subprocess.call(["screen","-dmS",wallet_name,path_to_cli_wallet,"-H",local_port,"-s",remote_ws,"--chain-id","16362d305df19018476052eed629bb4052903c7655a586a0e0cfbdb0eaf1bfd8"])

def unlockWallet():
    rpc.unlock(wallet_password)

def setPassword():
    rpc.set_password(wallet_password)

def importActiveKey():
    rpc.import_key(witnessname, private_active_key)

def getSigningKey():
    witness = rpc.get_witness(witnessname)
    signingKey = witness["signing_key"]
    return signingKey

def setSigningKey(signingKey):
    rpc.update_witness(witnessname,"",signingKey,"true")


def saveWallet():
    rpc.save_wallet_file(wallet.json)

def info():
    info = rpc.info()
    part = info["participation"]
    return part
