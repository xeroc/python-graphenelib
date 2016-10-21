from grapheneapi.grapheneclient import GrapheneClient
from pprint import pprint
from datetime import datetime
import time


class Config():
    wallet_host = "localhost"
    wallet_port = 8092
    witness_url = "ws://testnet.bitshares.eu/ws"
    broadcast = True


def formatTimeFromNow(secs=0):
    """ Properly Format Time that is `x` seconds in the future

        :param int secs: Seconds to go in the future (`x>0`) or the
                         past (`x<0`)
        :return: Properly formated time for Graphene (`%Y-%m-%dT%H:%M:%S`)
        :rtype: str

    """
    return datetime.utcfromtimestamp(
        time.time() + int(secs)).strftime('%Y-%m-%dT%H:%M:%S')

if __name__ == '__main__':

    creator = "xeroc"
    owner = "maker"
    amount = 15
    amount_asset = "PEG.FAKEUSD"
    zero_date = datetime.utcfromtimestamp(0).strftime('%Y-%m-%dT%H:%M:%S')

    policy = [1, {"vesting_seconds": 60 * 5,       # vesting period
                  "start_claim": formatTimeFromNow(10)
                  }]

#    policy = [ 0, {  # This is the time at which funds begin vesting
#                "begin_timestamp": formatTimeFromNow(60),
#                # No amount may be withdrawn before this many seconds
#                # of the vesting period have elapsed
#                "vesting_cliff_seconds": 10,
#                # Duration of the vesting period, in seconds. Must be
#                # greater than 0 and greater than vesting_cliff_seconds.
#                "vesting_duration_seconds": 60 * 60 * 5
#               }
#             ]

    client = GrapheneClient(Config)
    op = client.rpc.get_prototype_operation("vesting_balance_create_operation")
    creator = client.rpc.get_account(creator)
    owner = client.rpc.get_account(owner)
    asset = client.rpc.get_asset(amount_asset)
    op[1]['creator'] = creator["id"]
    op[1]['owner'] = owner["id"]
    op[1]['amount']["amount"] = int(amount * 10 ** asset["precision"])
    op[1]['amount']["asset_id"] = asset["id"]
    op[1]['policy'] = policy
    ops = [op]
    buildHandle = client.rpc.begin_builder_transaction()
    for op in ops:
        pprint(op)
        client.rpc.add_operation_to_builder_transaction(buildHandle, op)
    client.rpc.set_fees_on_builder_transaction(buildHandle, "1.3.0")
    tx = client.rpc.sign_builder_transaction(buildHandle, Config.broadcast)
    pprint(tx)
