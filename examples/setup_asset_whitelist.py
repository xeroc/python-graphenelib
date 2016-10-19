from grapheneapi.grapheneclient import GrapheneClient
from pprint import pprint


class Config():
    wallet_host           = "localhost"
    wallet_port           = 8092
    witness_url           = "wss://bitshares.openledger.info/ws"
    broadcast             = True


if __name__ == '__main__':

    asset = "TMPASSET"
    whitelist_accounts = ["null", "committee-account"]

    client = GrapheneClient(Config)
    asset = client.rpc.get_asset(asset)

    op = client.rpc.get_prototype_operation("asset_update_operation")
    op[1]["asset_to_update"] = asset["id"]
    op[1]["issuer"] = asset["issuer"]
    op[1]["new_options"] = asset["options"]

    whitelist_authorities = []
    for a in whitelist_accounts:
        ac = client.rpc.get_account(a)
        whitelist_authorities.append(ac["id"])

    op[1]["new_options"]["whitelist_authorities"] = whitelist_authorities
    buildHandle = client.rpc.begin_builder_transaction()
    client.rpc.add_operation_to_builder_transaction(buildHandle, op)
    client.rpc.set_fees_on_builder_transaction(buildHandle, "1.3.0")
    tx = client.rpc.sign_builder_transaction(buildHandle, Config.broadcast)
    pprint(tx)
