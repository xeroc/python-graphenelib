import requests
from grapheneapi import GrapheneClient
from grapheneexchange import GrapheneExchange
import json

#: Symbol to update the price fee of
asset_symbol = "ALTCAP"

#: array price feed producers (probably just one)
producers = ["altfund"]

######################################################################
# Feed price calculations for ALTCAP
######################################################################
# get coincap prices
# BTS $ "usdPrice"
# BTC $ "btcPrice"
coincap = requests.get('http://www.coincap.io/page/BTS')
coincap_usdBTS = float(coincap.json()["usdPrice"])
coincap_usdBTC = float(coincap.json()["btcPrice"])
coincap_btcCap = float(coincap.json()["btcCap"])
coincap_altCAP = float(coincap.json()["altCap"])

# print prices
print ('btcCap $',coincap_btcCap)
print ('altCap $',coincap_altCAP)
print ('')

# print prices
print ('BTC $',coincap_usdBTC)
print ('BTS $',coincap_usdBTS)
print ('')


# BTC:BTS  price
BTC_BTS = coincap_usdBTC / coincap_usdBTS
BTS_BTC = coincap_usdBTS / coincap_usdBTC

# print BTC BTS price 
print ('BTC:BTS  ',BTC_BTS)
print ('BTS:BTC  ',BTS_BTC)
print ('')


# price calculations
BTC_altcap_price = coincap_btcCap / coincap_altCAP
altcap_BTC_price = coincap_altCAP / coincap_btcCap

# print altcap ratio 
print ('ALTCAP:BTC  ',altcap_BTC_price)
print ('BTC:ALTCAP  ',BTC_altcap_price)
print ('')


# ALTCAP:BTS  price
ALTCAP_BTS = BTC_BTS / BTC_altcap_price
BTS_ALTCAP = BTC_altcap_price / BTC_BTS

# print ALTCAP:BTS price 
print ('ALTCAP:BTS  ',ALTCAP_BTS)
print ('BTS:ALTCAP  ',BTS_ALTCAP)
print ('')

######################################################################
# Feed 
######################################################################

#: Price denoted in  quote asset per backing asset
#: eg  2.0 SMART.TEST / TEST
price = BTC_altcap_price  # quote assets per backing asset

#: Scale the Core exchange rate
scale_cer = 0.95


#: Connection Settings
class Config():
	wallet_host           = "localhost"
	wallet_port           = 8092
	witness_url           = "ws://127.0.0.1:8090"
	user   = ""              # API user (optional)
	passwd = ""              # API user passphrase (optional)
	unlock = ""              # password to unlock the wallet if the cli-wallet is locked

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
                       "maintenance_collateral_ratio" : 1360,
                       "maximum_short_squeeze_ratio"  : 1069,
                       "core_exchange_rate": {
                       "quote": {"asset_id": "1.3.0",		# CER only works in BTS
                                 "amount": int(denominator * scale_cer / 1000)
                                 },
                       "base": {"asset_id": asset["id"],
                                "amount": numerator / BTC_BTS
                                }}}
        handle = graphene.rpc.begin_builder_transaction()
        op = [19,  # id 19 corresponds to price feed update operation
              {"asset_id"  : asset["id"],
               "feed"      : price_feed,
               "publisher" : account["id"]
               }]
        graphene.rpc.unlock(config.unlock)		# unlock your wallet
        graphene.rpc.add_operation_to_builder_transaction(handle, op)
        graphene.rpc.set_fees_on_builder_transaction(handle, "1.3.0")
        tx = graphene.rpc.sign_builder_transaction(handle, True)
        graphene.rpc.lock()					# lock your wallet
        print(json.dumps(tx, indent=4))

# print ALTCAP:BTS price 
print ('')
print ('ALTCAP:BTS  ',ALTCAP_BTS)
print ('BTS:ALTCAP  ',BTS_ALTCAP)
