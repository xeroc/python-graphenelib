import sys
import json
from grapheneapi import GrapheneWebsocket, GrapheneWebsocketProtocol
import time
import config
import subprocess

rpc = GrapheneWebsocket("localhost", config.rpc_port, "", "")
local_port = "127.0.0.1:" + config.rpc_port

def openProducer():
    subprocess.call(["screen","-dmS","wallet1","/home/user/src/bitshares-2/programs/cli_wallet/cli_wallet","-H","127.0.0.1:8093","-s","ws://192.241.239.195:8090","--chain-id","16362d305df19018476052eed629bb4052903c7655a586a0e0cfbdb0eaf1bfd8"])

def unlockWallet():
    rpc.unlock(config.wallet_password)

def setPassword():
    rpc.set_password(config.wallet_password)

def importActiveKey():
    rpc.import_key(config.witnessname, config.private_active_key)

def getSigningKey():
    witness = rpc.get_witness(config.witnessname)
    signingKey = witness["signing_key"]
    return signingKey

def setSigningKey(signingKey):
    rpc.update_witness(config.witnessname,"",signingKey,"true")


def saveWallet():
    rpc.save_wallet_file(wallet.json)

def info():
    info = rpc.info()
    part = info["participation"]
    return part
