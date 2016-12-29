from grapheneapi.grapheneclient import GrapheneClient
from pprint import pprint


class Config():
    wallet_host           = "localhost"
    wallet_port           = 8092
    witness_url           = "ws://testnet.bitshares.eu/ws"
    broadcast             = True


def formatTimeFromNow(secs=0):
    from datetime import datetime
    import time
    """ Properly Format Time that is `x` seconds in the future

        :param int secs: Seconds to go in the future (`x>0`) or the
                         past (`x<0`)
        :return: Properly formated time for Graphene (`%Y-%m-%dT%H:%M:%S`)
        :rtype: str

    """
    return datetime.utcfromtimestamp(time.time() + int(secs)).strftime('%Y-%m-%dT%H:%M:%S')

if __name__ == '__main__':

    authorized_account    = "xeroc"
    withdraw_from_account = "maker"
    period_start_time     = formatTimeFromNow(+60)
    withdrawal_period_sec = 60 * 60 * 24 * 30
    periods_until_expiration = 12 * 15
    withdrawal_limit_asset = "PEG.FAKEUSD"
    withdrawal_limit_amount = 100

    client = GrapheneClient(Config)
    op = client.rpc.get_prototype_operation("withdraw_permission_create_operation")
    authorized_account    = client.rpc.get_account(authorized_account)
    withdraw_from_account = client.rpc.get_account(withdraw_from_account)
    op[1]['authorized_account'] = authorized_account["id"]
    op[1]['period_start_time'] = period_start_time
    op[1]['withdrawal_period_sec'] = withdrawal_period_sec
    op[1]['periods_until_expiration'] = periods_until_expiration
    op[1]['withdraw_from_account'] = withdraw_from_account["id"]
    op[1]['withdrawal_limit'] = {'amount': int(withdrawal_limit_amount * 10 ** client.rpc.get_asset(withdrawal_limit_asset)["precision"]),
                                 'asset_id': client.rpc.get_asset(withdrawal_limit_asset)["id"]}
    ops = [op]
    buildHandle = client.rpc.begin_builder_transaction()
    for op in ops :
        pprint(op)
        client.rpc.add_operation_to_builder_transaction(buildHandle, op)
    client.rpc.set_fees_on_builder_transaction(buildHandle, "1.3.0")
    tx = client.rpc.sign_builder_transaction(buildHandle, Config.broadcast)
    pprint(tx)
