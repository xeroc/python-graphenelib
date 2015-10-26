import sys
import json
from grapheneapi import GrapheneWebsocket, GrapheneWebsocketProtocol
import time
import config
import subprocess

rpc = GrapheneWebsocket("localhost", config.rpc_port, "", "")
local_port = "127.0.0.1:" + config.rpc_port

def openProducer():
    subprocess.call(["screen","-dmS","wallet"+config.producer_number,config.path_to_cli_wallet,"-H",local_port,"-s",config.remote_ws])

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
