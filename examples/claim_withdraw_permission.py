from grapheneapi.grapheneclient import GrapheneClient
from pprint import pprint


class Config():
    wallet_host           = "localhost"
    wallet_port           = 8092
    witness_url           = "ws://testnet.bitshares.eu/ws"
    broadcast             = True


def claim_from_withdraw_permission(rpc,
                                   withdraw_permission,
                                   amount_to_withdraw,
                                   asset_to_widthdraw,
                                   withdraw_from_account,
                                   withdraw_to_account,
                                   broadcast=True):

    op = rpc.get_prototype_operation("withdraw_permission_claim_operation")
    withdraw_from_account = rpc.get_account(withdraw_from_account)
    withdraw_to_account = rpc.get_account(withdraw_to_account)
    op[1]['amount_to_withdraw'] = {'amount': int(amount_to_withdraw * 10 ** rpc.get_asset(asset_to_widthdraw)["precision"]),
                                   'asset_id': rpc.get_asset(asset_to_widthdraw)["id"]}
    op[1]['withdraw_permission'] = withdraw_permission
    op[1]['withdraw_from_account'] = withdraw_from_account["id"]
    op[1]['withdraw_to_account'] = withdraw_to_account["id"]
    buildHandle = rpc.begin_builder_transaction()
    rpc.add_operation_to_builder_transaction(buildHandle, op)
    rpc.set_fees_on_builder_transaction(buildHandle, "1.3.0")
    return rpc.sign_builder_transaction(buildHandle, broadcast)

if __name__ == '__main__':

    asset_to_widthdraw    = "PEG.FAKEUSD"
    amount_to_withdraw    = 100
    withdraw_permission   = "1.12.0"
    withdraw_from_account = "maker"
    withdraw_to_account   = "xeroc"

    client = GrapheneClient(Config)
    tx = claim_from_withdraw_permission(client.rpc, withdraw_permission, amount_to_withdraw, asset_to_widthdraw, withdraw_from_account, withdraw_to_account)
    pprint(tx)
