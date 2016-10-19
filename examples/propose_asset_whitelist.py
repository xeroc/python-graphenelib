from grapheneapi.grapheneclient import GrapheneClient
from pprint import pprint


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


class Config():
    wallet_host           = "localhost"
    wallet_port           = 8092
    broadcast             = True


if __name__ == '__main__':
    expiration = formatTimeFromNow(60 * 60 * 24)
    proposer = "fabian"
    asset = "TMP"
    whitelist_accounts = ["tmp-asset-issuer"]

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
    client.rpc.propose_builder_transaction2(buildHandle, proposer, expiration, 0, False)
    client.rpc.set_fees_on_builder_transaction(buildHandle, "1.3.0")
    tx = client.rpc.sign_builder_transaction(buildHandle, True)
    pprint(tx)
