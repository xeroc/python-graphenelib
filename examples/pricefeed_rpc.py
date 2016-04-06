"""
    This example shows how to create a price feed and publish it using
    a RPC connection to a running cli_wallet. Hence, the cli_wallet
    provides the private key and signing capabilities

"""
from grapheneapi import GrapheneClient
from grapheneexchange import GrapheneExchange
import json

#: Symbol to update the price fee of
asset_symbol = "SMART.TEST"

#: array price feed prodicers (probably just one)
producers = ["xeroc"]

#: Price denoted in  quote asset per backing asset
#: e.g.  2.0 SMART.TEST / TEST
price = 2.0  # quote assets per backing asset

#: Scale the Core exchange rate
scale_cer = 1.05


#: Connetion Settings
class Config():
    wallet_host           = "localhost"
    wallet_port           = 8092
    witness_url           = "ws://testnet.bitshares.eu/ws"

if __name__ == '__main__':
    config = Config
    graphene = GrapheneClient(config)

    asset = graphene.rpc.get_asset(asset_symbol)
    bitasset_data = graphene.getObject(asset["bitasset_data_id"])
    base = graphene.getObject(bitasset_data["options"]["short_backing_asset"])
    # Correct for different precisions of base and quote assets
    price = price * 10 ** asset["precision"] / 10 ** base["precision"]

    # convert into a fraction
    denominator = 10 ** base["precision"]
    numerator   = int(price * 10 ** base["precision"])

    for producer in producers:
        account = graphene.rpc.get_account(producer)
        price_feed  = {"settlement_price": {
                       "quote": {"asset_id": base["id"],
                                 "amount": denominator
                                 },
                       "base": {"asset_id": asset["id"],
                                "amount": numerator
                                }
                       },
                       "maintenance_collateral_ratio" : 1200,
                       "maximum_short_squeeze_ratio"  : 1100,
                       "core_exchange_rate": {
                       "quote": {"asset_id": base["id"],
                                 "amount": int(denominator * scale_cer)
                                 },
                       "base": {"asset_id": asset["id"],
                                "amount": numerator
                                }}}
        handle = graphene.rpc.begin_builder_transaction()
        op = [19,  # id 19 corresponds to price feed update operation
              {"asset_id"  : asset["id"],
               "feed"      : price_feed,
               "publisher" : account["id"]
               }]
        graphene.rpc.add_operation_to_builder_transaction(handle, op)
        graphene.rpc.set_fees_on_builder_transaction(handle, "1.3.0")
        tx = graphene.rpc.sign_builder_transaction(handle, True)
        print(json.dumps(tx, indent=4))
