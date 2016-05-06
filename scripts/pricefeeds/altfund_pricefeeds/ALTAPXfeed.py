import json

import requests
from grapheneapi import GrapheneClient


# : Symbol to update the price fee of
asset_symbol = "ALTCAP.X"

# : array price feed producers (probably just one)
producers = ["altfund"]

# #####################################################################
# Feed price calculations for ALTCAP
# #####################################################################

btcCaps = []
altxCaps = []
usdBTCs = []
usdBTSs = []

# get coincap prices
try:
    coincap_front = requests.get('http://www.coincap.io/front').json()
    coincap_global = requests.get('http://www.coincap.io/global').json()
    coincap = requests.get('http://www.coincap.io/page/BTS').json()
    coincap_alts_capsX = [float(coin['mktcap']) for coin in coincap_front if
                          'position24' in coin and int(coin['position24']) <= 11 and coin['short'] != "BTC"]
    coincap_altCapX = sum(coincap_alts_capsX)
    coincap_btcCap = float(coincap_global["btcCap"])
except Exception as e:
    print("Something went wrong while getting the data from coincap")
    print(e)
else:
    btcCaps.append(coincap_btcCap)
    altxCaps.append(coincap_altCapX)
    usdBTSs.append(float(coincap["usdPrice"]))
    usdBTCs.append(float(coincap["btcPrice"]))

try:
    cmc_ticker = requests.get('https://api.coinmarketcap.com/v1/ticker/').json()
    cmc_alts_capsX = [float(coin['market_cap_usd']) for coin in cmc_ticker if
                      coin['rank'] <= 11 and coin['symbol'] != "BTC"]
    cmc_altCapX = sum(cmc_alts_capsX)
    cmc_btcCap = next((coin['market_cap_usd'] for coin in cmc_ticker if coin["symbol"] == "BTC"))

    usdBTCs.append(next((coin['price_usd'] for coin in cmc_ticker if coin["symbol"] == "BTC")))
    usdBTSs.append(next((coin['price_usd'] for coin in cmc_ticker if coin["symbol"] == "BTS")))
except Exception as e:
    print("Something went wrong while getting the data from coinmarketcap")
    print(e)
else:
    btcCaps.append(cmc_btcCap)
    altxCaps.append(cmc_altCapX)

if len(btcCaps) != 0:
    btcCapsAverage = sum(btcCaps) / len(btcCaps)
    altCapsAverage = sum(altxCaps) / len(altxCaps)
else:
    raise Exception("No pricefeeds")

if len(usdBTSs) != 0:
    usdBTC_average = sum(usdBTCs) / len(usdBTCs)
    usdBTS_average = sum(usdBTSs) / len(usdBTSs)
    BTC_BTS = usdBTC_average / usdBTS_average
    BTS_BTC = usdBTS_average / usdBTC_average
else:
    raise Exception("No pricefeeds")

BTC_altcap_price = btcCapsAverage / altCapsAverage
altcap_BTC_price = altCapsAverage / btcCapsAverage

print('BTC caps:', btcCaps, 'average:', btcCapsAverage)
print('ALT caps:', altxCaps, 'average:', altCapsAverage)
print('')

print('ALTCAP:BTC  ', altcap_BTC_price)
print('BTC:ALTCAP  ', BTC_altcap_price)
print('')

# print BTC BTS price
print('BTC:BTS  ', BTC_BTS)
print('BTS:BTC  ', BTS_BTC)
print('')

# ALTCAP:BTS  price
ALTCAP_BTS = BTC_BTS / BTC_altcap_price
BTS_ALTCAP = BTC_altcap_price / BTC_BTS


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
    wallet_host = "localhost"
    wallet_port = 8092
    witness_url = "ws://127.0.0.1:8090"
    user = ""  # API user (optional)
    passwd = ""  # API user passphrase (optional)
    unlock = ""  # password to unlock the wallet if the cli-wallet is locked


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
    numerator = int(price * 10 ** base["precision"])

    for producer in producers:
        account = graphene.rpc.get_account(producer)
        price_feed = {"settlement_price": {
            "quote": {"asset_id": base["id"],
                      "amount": denominator
            },
            "base": {"asset_id": asset["id"],
                     "amount": numerator
            }
        },
                      "maintenance_collateral_ratio": 1360,
                      "maximum_short_squeeze_ratio": 1069,
                      "core_exchange_rate": {
                          "quote": {"asset_id": "1.3.0",  # CER only works in BTS
                                    "amount": int(denominator * scale_cer / 1000)
                          },
                          "base": {"asset_id": asset["id"],
                                   "amount": numerator / BTC_BTS
                          }}}
        handle = graphene.rpc.begin_builder_transaction()
        op = [19,  # id 19 corresponds to price feed update operation
              {"asset_id": asset["id"],
               "feed": price_feed,
               "publisher": account["id"]
              }]
        graphene.rpc.unlock(config.unlock)  # unlock your wallet
        graphene.rpc.add_operation_to_builder_transaction(handle, op)
        graphene.rpc.set_fees_on_builder_transaction(handle, "1.3.0")
        tx = graphene.rpc.sign_builder_transaction(handle, True)
        graphene.rpc.lock()  # lock your wallet
        print(json.dumps(tx, indent=4))

# print ALTCAP:BTS price
print('')
print('ALTCAP:BTS  ', ALTCAP_BTS)
print('BTS:ALTCAP  ', BTS_ALTCAP)
