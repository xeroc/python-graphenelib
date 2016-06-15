from grapheneapi import GrapheneClient
from grapheneexchange import GrapheneExchange
from graphenebase import transactions
from pprint import pprint

issuer = "xeroc"
from_account = "maker"
to_account = "xeroc"
asset = "LIVE"
amount = 100.0
wifs = ["<active-wif-key-of-issuer>"]
witness_url = "ws://testnet.bitshares.eu/ws"


def constructSignedTransaction(ops):
    ops        = transactions.addRequiredFees(client.ws, ops, "1.3.0")
    ref_block_num, ref_block_prefix = transactions.getBlockParams(client.ws)
    expiration = transactions.formatTimeFromNow(30)
    tx = transactions.Signed_Transaction(
        ref_block_num=ref_block_num,
        ref_block_prefix=ref_block_prefix,
        expiration=expiration,
        operations=ops
    )
    w          = tx.sign(wifs, chain=client.getChainInfo())
    return w


#: Connetion Settings
class Config():
    witness_url           = witness_url


if __name__ == '__main__':
    config = Config
    client = GrapheneClient(config)

    issuer = client.ws.get_account(issuer)
    from_account = client.ws.get_account(from_account)
    to_account = client.ws.get_account(to_account)
    asset = client.ws.get_asset(asset)
    amount = int(amount * 10 ** asset["precision"])

    ops = []
    op = transactions.Override_transfer(**{
        "fee": {"amount": 0,
                "asset_id": "1.3.0"},
        "issuer": issuer["id"],
        "from": from_account["id"],
        "to": to_account["id"],
        "amount": {"amount": amount,
                   "asset_id": asset["id"]},
        "extensions": []
    })
    ops.append(transactions.Operation(op))

    tx = constructSignedTransaction(ops)
    pprint(transactions.JsonObj(tx))
    print(client.ws.broadcast_transaction(transactions.JsonObj(tx), api="network_broadcast"))
