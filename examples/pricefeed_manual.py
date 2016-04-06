"""
    This example shows how to create a price feed and publish it only
    using a websocket connect to a full node. Hence, the author needs to
    provide the private key in the script and python performs the
    signing of the transaction

"""
from grapheneapi import GrapheneClient
from grapheneexchange import GrapheneExchange
from graphenebase import transactions
from pprint import pprint

#: Symbol to update the price fee of
asset_symbol = "SMART.TEST"

#: array price feed prodicers (probably just one)
producers = ["xeroc"]

#: Price denoted in  quote asset per backing asset
#: e.g.  2.0 SMART.TEST / TEST
price = 2.0  # quote assets per backing asset

#: Scale the Core exchange rate
scale_cer = 1.05

#: List of private keys to use to sign the transaction
#: I.e. the active private keys of all producers
wifs = ["<active-wif-keys-of-produsers>"]


#: Connetion Settings
class Config():
    witness_url           = "ws://testnet.bitshares.eu/ws"


def constructSignedTransaction(ops):
    ops        = transactions.addRequiredFees(client.ws, ops, "1.3.0")
    ref_block_num, ref_block_prefix = transactions.getBlockParams(client.ws)
    expiration = transactions.formatTimeFromNow(30)
    signed     = transactions.Signed_Transaction(ref_block_num, ref_block_prefix, expiration, ops)

    pprint(transactions.JsonObj(signed))
    w          = signed.sign(wifs, chain=client.getChainInfo())
    return w


if __name__ == '__main__':
    config = Config
    client = GrapheneClient(config)

    asset = client.ws.get_asset(asset_symbol)
    bitasset_data = client.getObject(asset["bitasset_data_id"])
    base = client.getObject(bitasset_data["options"]["short_backing_asset"])

    # Correct for different precisions of base and quote assets
    price = price * 10 ** asset["precision"] / 10 ** base["precision"]

    # convert into a fraction
    denominator = int(10 ** base["precision"])
    numerator   = int(price * 10 ** base["precision"])

    ops = []
    for producer in producers:
        account = client.ws.get_account(producer)
        feed = transactions.PriceFeed(**{
            "settlement_price" : transactions.Price(
                base=transactions.Asset(amount=numerator, asset_id=asset["id"]),
                quote=transactions.Asset(amount=denominator, asset_id=base["id"]),
            ),
            "core_exchange_rate" : transactions.Price(
                base=transactions.Asset(amount=numerator, asset_id=asset["id"]),
                quote=transactions.Asset(amount=denominator * scale_cer, asset_id=base["id"]),
            ),
            "maximum_short_squeeze_ratio" : 1200,
            "maintenance_collateral_ratio" : 1100,
        })
        pFeed = transactions.Asset_publish_feed(
            fee=transactions.Asset(amount=0, asset_id="1.3.0"),
            publisher=account["id"],
            asset_id=asset["id"],
            feed=feed
        )
        ops.append(transactions.Operation(pFeed))

    tx = constructSignedTransaction(ops)
    print(tx)
    print(client.ws.broadcast_transaction(transactions.JsonObj(tx), api="network_broadcast"))
