from grapheneapi.grapheneclient import GrapheneClient
import json
from pprint import pprint
from datetime import datetime
import time


class Config():
    wallet_host           = "localhost"
    wallet_port           = 8092
    witness_url           = "wss://bitshares.openledger.info/ws"

    drain                 = "<asset>"
    account               = "<asset-issuer>"


def formatTimeFromNow(secs=0):
    return datetime.utcfromtimestamp(time.time() + int(secs)).strftime('%Y-%m-%dT%H:%M:%S')


if __name__ == '__main__':
    config = Config
    client = GrapheneClient(config)

    account = client.rpc.get_account(config.account)
    asset = client.rpc.get_asset(config.drain)
    assetdyn = client.getObject(asset["dynamic_asset_data_id"])
    fee_pool = int(assetdyn["fee_pool"]) / 10 ** client.getObject("1.3.0")["precision"]

    op = client.rpc.get_prototype_operation("limit_order_create_operation")
    op[1]["fee"]["amount"] = int(fee_pool * 10 ** asset["precision"])
    op[1]["fee"]["asset_id"] = asset["id"]
    op[1]["seller"] = account["id"]
    op[1]["amount_to_sell"]["amount"] = 1
    op[1]["amount_to_sell"]["asset_id"] = asset["id"]
    op[1]["min_to_receive"]["amount"] = 1
    op[1]["min_to_receive"]["asset_id"] = "1.3.0"
    op[1]["expiration"] = formatTimeFromNow(60 * 60 * 12)

    buildHandle = client.rpc.begin_builder_transaction()
    client.rpc.add_operation_to_builder_transaction(buildHandle, op)
    tx = client.rpc.sign_builder_transaction(buildHandle, True)
    pprint(tx)
