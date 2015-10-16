#!/usr/bin/env python3
# coding=utf8 sw=1 expandtab ft=python

####################################################################################
#########################  W  A  R  N  I  N  G   ###################################
####################################################################################
##                                                                                ##
## This is EXPERIMENTAL code!!                                                    ##
##                                                                                ##
## If you are a witness capable of publishing a price feed for                    ##
## market pegged assets, you should carefully REVIEW this code in order to        ##
## not publish a wrong price that may                                             ##
##                                                                                ##
##              a) result in erroneous margin calls, or a                         ##
##              b) black swan event                                               ##
##                                                                                ##
## for one or more assets.                                                        ##
##                                                                                ##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR     ##
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,       ##
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE    ##
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER         ##
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,  ##
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN      ##
## THE SOFTWARE.                                                                  ##
##                                                                                ##
####################################################################################

import requests
import json
import sys
import time
import statistics
import re
import numpy as num
import sys
import config
import threading
import fractions
from prettytable import PrettyTable
from math        import fabs
from pprint      import pprint
from datetime    import datetime
from grapheneapi import GrapheneAPI

## ----------------------------------------------------------------------------
## When do we have to force publish?
## ----------------------------------------------------------------------------
def publish_rule():
 ##############################################################################
 # - if you haven't published a price in the past 20 minutes
 # - if REAL_PRICE < MEDIAN and YOUR_PRICE > MEDIAN publish price
 # - if REAL_PRICE > MEDIAN and YOUR_PRICE < MEDIAN and abs( YOUR_PRICE - REAL_PRICE ) / REAL_PRICE > 0.005 publish price
 # The goal is to force the price down rapidly and allow it to creep up slowly.
 # By publishing prices more often it helps market makers maintain the peg and
 # minimizes opportunity for shorts to sell USD below the peg that the market
 # makers then have to absorb.
 # If we can get updates flowing smoothly then we can gradually reduce the spread in the market maker bots.
 # *note: all prices in USD per BTS
 # if you haven't published a price in the past 20 minutes, and the price change more than 0.5%
 ##############################################################################
 # YOUR_PRICE = Your current published price.                    = myCurrentFeed[asset]
 # REAL_PRICE = Lowest of external feeds                         = realPrice
 # MEDIAN = current median price according to the blockchain.    = price_median_blockchain[asset]
 ##############################################################################
 for asset in asset_list_publish :
  ## Define REAL_PRICE
  realPrice = statistics.median( price["BTS"][asset] )
  ## Rules
  if (datetime.utcnow()-lastUpdate[asset]).total_seconds() > config.maxAgeFeedInSeconds :
        print("Feeds for %s too old! Force updating!" % asset)
        return True
  elif realPrice     < price_median_blockchain[asset] and \
       myCurrentFeed[asset] > price_median_blockchain[asset]:
        print("External price move for %s: realPrice(%.8f) < feedmedian(%.8f) and newprice(%.8f) > feedmedian(%f) Force updating!"\
               % (asset,realPrice,price_median_blockchain[asset],realPrice,price_median_blockchain[asset]))
        return True
  elif fabs(myCurrentFeed[asset]-realPrice)/realPrice > config.change_min and\
       (datetime.utcnow()-lastUpdate[asset]).total_seconds() > config.maxAgeFeedInSeconds > 20*60:
        print("New Feeds differs too much for %s %.8f > %.8f! Force updating!" \
               % (asset,fabs(myCurrentFeed[asset]-realPrice), config.change_min))
        return True
 ## default: False
 return False

## ----------------------------------------------------------------------------
## Fetch data
## ----------------------------------------------------------------------------
def fetch_from_yunbi():
  global price, volume
  try :
   url="https://yunbi.com/api/v2/tickers.json"
   response = requests.get(url=url, headers=_request_headers, timeout=3)
   result = response.json()
  except Exception as e:
   print("\nError fetching results from yunbi! ({0})\n".format(str(e)))
   if config.yunbi_trust_level > 0.8:
    sys.exit("\nExiting due to exchange importance\n")
   return

  availableAssets = [ core_symbol ]
  for coin in availableAssets :
   if float(result[coin.lower()+"btc"]["ticker"]["last"]) < config.minValidAssetPriceInBTC:
    print("\nUnreliable results from yunbi for %s"%(coin))
    continue
   price["BTC"][ coin ].append(float(result[coin.lower()+"btc"]["ticker"]["last"]))
   volume["BTC"][ coin ].append(float(result[coin.lower()+"btc"]["ticker"]["vol"])*config.yunbi_trust_level)

  availableAssets = [ core_symbol, "BTC" ]
  for coin in availableAssets :
   if float(result[coin.lower()+"cny"]["ticker"]["last"]) < config.minValidAssetPriceInBTC:
    print("Unreliable results from yunbi for %s"%(coin))
    continue
   price["CNY"][ coin ].append(float(result[coin.lower()+"cny"]["ticker"]["last"]))
   volume["CNY"][ coin ].append(float(result[coin.lower()+"cny"]["ticker"]["vol"])*config.yunbi_trust_level)

def fetch_from_btc38():
  global price, volume
  url="http://api.btc38.com/v1/ticker.php"
  availableAssets = [ core_symbol ]
  try :
   params = { 'c': 'all', 'mk_type': 'btc' }
   response = requests.get(url=url, params=params, headers=_request_headers, timeout=3 )
   result = response.json()
  except Exception as e:
   print("\nError fetching results from btc38! ({0})\n".format(str(e)))
   if config.btc38_trust_level > 0.8:
    sys.exit("\nExiting due to exchange importance!\n")
   return

  for coin in availableAssets :
   if "ticker" in result[coin.lower()] and result[coin.lower()]["ticker"] and float(result[coin.lower()]["ticker"]["last"])>config.minValidAssetPriceInBTC:
    price["BTC"][ coin ].append(float(result[coin.lower()]["ticker"]["last"]))
    volume["BTC"][ coin ].append(float(result[coin.lower()]["ticker"]["vol"]*result[coin.lower()]["ticker"]["last"])*config.btc38_trust_level)

  availableAssets = [ core_symbol, "BTC" ]
  try :
   params = { 'c': 'all', 'mk_type': 'cny' }
   response = requests.get(url=url, params=params, headers=_request_headers, timeout=3 )
   result = response.json()
  except Exception as e:
   print("\nError fetching results from btc38! ({0})\n".format(str(e)))
   if config.btc38_trust_level > 0.8:
    sys.exit("\nExiting due to exchange importance!\n")
   return

  for coin in availableAssets:
   if "ticker" in result[coin.lower()] and result[coin.lower()]["ticker"]  and float(result[coin.lower()]["ticker"]["last"])>config.minValidAssetPriceInBTC:
    price["CNY"][ coin ].append(float(result[coin.lower()]["ticker"]["last"]))
    volume["CNY"][ coin ].append(float(result[coin.lower()]["ticker"]["vol"])*float(result[coin.lower()]["ticker"]["last"])*config.btc38_trust_level)

def fetch_from_bter():
  global price, volume
  try :
   url="http://data.bter.com/api/1/tickers"
   response = requests.get(url=url, headers=_request_headers, timeout=3 )
   result = response.json()

  except Exception as e:
   print("\nError fetching results from bter! ({0})\n".format(str(e)))
   if config.bter_trust_level > 0.8:
    sys.exit("\nExiting due to exchange importance\n")
   return

  availableAssets = [ "BTC", core_symbol ]
  for market in ["BTC", "CNY", "USD"] :
   for coin in availableAssets :
    if coin == market : continue
    if float(result[coin.lower()+"_"+market.lower()]["last"]) < config.minValidAssetPriceInBTC:
     print("Unreliable results from bter for %s"%(coin))
     continue
    price[market][coin].append(float(result[coin.lower()+"_"+market.lower()]["last"]))
    volume[market][coin].append(float(result[coin.lower()+"_"+market.lower()]["vol_"+market.lower()])*config.bter_trust_level)

def fetch_from_poloniex():
  global price, volume
  try:
   url="https://poloniex.com/public?command=returnTicker"
   response = requests.get(url=url, headers=_request_headers, timeout=3 )
   result = response.json()
   availableAssets = [ core_symbol ]
  except Exception as e:
   print("\nError fetching results from poloniex! ({0})\n".format(str(e)))
   if config.poloniex_trust_level > 0.8:
    sys.exit("\nExiting due to exchange importance!\n")
   return
  for coin in availableAssets :
   if float(result["BTC_"+coin]["last"]) > config.minValidAssetPriceInBTC:
    price["BTC"][ coin ].append(float(result["BTC_"+coin]["last"]))
    volume["BTC"][ coin ].append(float(result["BTC_"+coin]["baseVolume"])*config.poloniex_trust_level)

def fetch_from_bittrex():
  availableAssets = [ "BTSX" ]
  try:
   url="https://bittrex.com/api/v1.1/public/getmarketsummaries"
   response = requests.get(url=url, headers=_request_headers, timeout=3 )
   result = response.json()["result"]
  except Exception as e:
   print("\nError fetching results from bittrex! ({0})\n".format(str(e)))
   if config.bittrex_trust_level > 0.8:
    sys.exit("\nExiting due to exchange importance!\n")
   return
  for coin in result :
   if( coin[ "MarketName" ] in ["BTC-"+a for a in availableAssets] ) :
    mObj    = re.match( 'BTC-(.*)', coin[ "MarketName" ] )
    altcoin = mObj.group(1)
    coinmap=altcoin
    if altcoin=="BTSX" :
     coinmap=core_symbol
    if float(coin["Last"]) > config.minValidAssetPriceInBTC:
     price["BTC"][ coinmap ].append(float(coin["Last"]))
     volume["BTC"][ coinmap ].append(float(coin["Volume"])*float(coin["Last"])*config.bittrex_trust_level)

def fetch_from_yahoo():
  global price, volume
  try :
   # Currencies and commodities
   for base in _yahoo_base :
    yahooAssets = ",".join([a+base+"=X" for a in _yahoo_quote])
    url="http://download.finance.yahoo.com/d/quotes.csv"
    params = {'s':yahooAssets,'f':'l1','e':'.csv'}
    response = requests.get(url=url, headers=_request_headers, timeout=3 ,params=params)
    yahooprices =  response.text.replace('\r','').split( '\n' )
    for i,a in enumerate(_yahoo_quote) :
     if float(yahooprices[i]) > 0 :
      price[base][ bts_yahoo_map(a) ].append(float(yahooprices[i]))
      volume[base][ bts_yahoo_map(a) ].append(float(1))

   # indices
   yahooAssets = ",".join(_yahoo_indices.keys())
   url="http://download.finance.yahoo.com/d/quotes.csv"
   params = {'s':yahooAssets,'f':'l1','e':'.csv'}
   response = requests.get(url=url, headers=_request_headers, timeout=3 ,params=params)
   yahooprices =  response.text.replace('\r','').split( '\n' )
   for i,a in enumerate(_yahoo_indices) :
    if float(yahooprices[i]) > 0 :
     #price[ list(_yahoo_indices.values())[i] ][ bts_yahoo_map(a) ].append(float(yahooprices[i]))
     price[ core_symbol ][ bts_yahoo_map(a) ].append(1/float(yahooprices[i]))
     volume[ core_symbol ][ bts_yahoo_map(a) ].append(1.0)

  except Exception as e:
    sys.exit("\nError fetching results from yahoo! {0}".format(str(e)))

def fetch_bitcoinaverage():
   global price, volume
   url="https://api.bitcoinaverage.com/ticker/"
   availableAssets = [ "USD", "EUR" ]
   for coin in availableAssets :
    response = requests.get(url=url+coin, headers=_request_headers, timeout=3)
    result = response.json()
    price[coin][ "BTC" ].append(float(result["last"]))
    volume[coin][ "BTC" ].append(float(result["total_vol"]))

## ----------------------------------------------------------------------------
## Fetch current feeds, assets and feeds of assets from wallet
## ----------------------------------------------------------------------------
def fetch_from_wallet(rpc):
 print("Fetching data from wallet...")
 ## Get my Witness
 myWitness = rpc.get_witness(config.delegate_name)
 witnessId = myWitness["witness_account"]

 ## asset definition - mainly for precision
 for asset in asset_list_publish + ["1.3.0"]:
  a = rpc.get_asset(asset)
  assets[ asset ] = a  # resolve SYMBOL
  assets[ a["id"] ] = a # resolve id

 for asset in asset_list_publish :
  ## feeds for asset
  result = rpc.get_bitasset_data(asset)
  # default
  price_median_blockchain[asset] = 0.0
  myCurrentFeed[asset] = -1.0
  lastUpdate[asset] = datetime.fromtimestamp(0)

  try :
   ## get current feed data
   base  = result["current_feed"]["settlement_price"]["base"]
   quote = result["current_feed"]["settlement_price"]["quote"]
   assert base is not "1.3.0"
   base_precision  = assets[  base["asset_id"] ]["precision"]
   quote_precision = assets[ quote["asset_id"] ]["precision"]
   base_price  = (int(base["amount"] )/10**base_precision )
   quote_price = (int(quote["amount"])/10**quote_precision)
   price_median_blockchain[asset] = float(base_price/quote_price)
   # (base should be 1.3.0( BTS) hence price is x USD/BTS)

   ## my feed specifics
   found = False
   for feed in result["feeds"] :
    if feed[0] == witnessId :
     found = True
     lastUpdate[asset] = datetime.strptime(feed[1][0],"%Y-%m-%dT%H:%M:%S")
     base  = feed[1][1]["settlement_price"]["base"]
     quote = feed[1][1]["settlement_price"]["quote"]
     assert base is not "1.3.0"
     base_price  = (int(base["amount"] )/10**base_precision )
     quote_price = (int(quote["amount"])/10**quote_precision)
     myCurrentFeed[asset] = float(base_price/quote_price)
     break;
  except ZeroDivisionError :
   print("No price feeds for asset %s available on the blockchain, yet!" % asset)

## ----------------------------------------------------------------------------
## Send the new feeds!
## ----------------------------------------------------------------------------
def update_feed(rpc, myassets):
 wallet_was_unlocked = False

 if rpc.is_locked() :
  wallet_was_unlocked = True
  print( "Unlocking wallet" )
  ret = rpc.unlock(config.unlock)

 print("publishing feeds for delegate: %s"%config.delegate_name)
 for a in myassets :
  result = rpc.publish_asset_feed(config.delegate_name, a[0], a[1], True) # True: sign+broadcast

 if wallet_was_unlocked :
  print( "Relocking wallet" )
  rpc.lock()

## ----------------------------------------------------------------------------
## calculate feed prices in BTS for all assets given the exchange prices in USD,CNY,BTC,...
## ----------------------------------------------------------------------------
def derive_prices():
 # Invert pairs
 for base in _bases :
  for quote in _bases :
   if base == quote : continue
   for idx in range(0, len(price[base][quote])) :
     price[quote][base].append( (float(1/price[base][quote][idx] )))
     #volume[quote][base].append((float(1/volume[base][quote][idx])))

 # derive BTS prices for all _base assets
 for base in _bases :
  for quote in _bases :
   if base == quote : continue
   for ratio in price[base][quote] :
    for idx in range(0, len(price[base]["BTS"])) :
     price[quote]["BTS"].append( (float(price[base]["BTS"][idx] /ratio)))
     #volume[quote]["BTS"].append((float(volume[base]["BTS"][idx]/ratio)))

 for base in _bases :
  for quote in asset_list_publish :
   for ratio in price[ base ][ quote ] :
    for idx in range(0, len(price[base]["BTS"])) :
     price["BTS"][quote].append( (float(price[base]["BTS"][idx] /ratio)))
     #volume["BTS"][quote].append((float(volume[base]["BTS"][idx]/ratio)))

 for asset in asset_list_publish :
  ### Median
  try :
   price_in_bts_weighted[asset] = statistics.median(price[core_symbol][asset])
  except Exception as e:
   print("Error in asset %s: %s" %(asset, str(e)))

  ### Mean
  #price_in_bts_weighted[asset] = statistics.mean(price[core_symbol][asset])

  ### Weighted Mean
  #assetvolume= [v for v in  volume[core_symbol][asset] ]
  #assetprice = [p for p in  price[core_symbol][asset]  ]
  #if len(assetvolume) > 1 :
  # price_in_bts_weighted[asset] = num.average(assetprice, weights=assetvolume)
  #else :
  # price_in_bts_weighted[asset] = assetprice[0]

  ### Discount
  price_in_bts_weighted[asset] = price_in_bts_weighted[asset] * config.discount

## ----------------------------------------------------------------------------
## Print stats as table
## ----------------------------------------------------------------------------
def print_stats() :
 t = PrettyTable(["asset","BTS/base","my mean","median exchanges","blockchain median","% change (my)","% change (blockchain)","last update"])
 t.align                   = 'r'
 t.border                  = True
 t.float_format['BTS/base']              = ".8"
 t.float_format['my mean']               = ".8"
 t.float_format['median exchanges']      = ".8"
 t.float_format['blockchain median']     = ".8"
 t.float_format['% change (my)']         = ".5"
 t.float_format['% change (blockchain)'] = ".5"
 #t.align['BTC']            = "r"
 for asset in asset_list_publish :
    if len(price[core_symbol][asset]) < 1 : continue # empty asset
    age                     = (str(datetime.utcnow()-lastUpdate[asset]))
    weighted_external_price = price_in_bts_weighted[asset]
    prices_from_exchanges   = price[core_symbol][asset]
    price_from_blockchain   = price_median_blockchain[asset]
    cur_feed                = float(myCurrentFeed[asset])
    ## Stats
    mean_exchanges          = statistics.mean(prices_from_exchanges)
    median_exchanges        = statistics.median(prices_from_exchanges)
    if cur_feed == 0 :               change_my              = -1
    else :                           change_my              = ((weighted_external_price - cur_feed)/cur_feed)*100
    if price_from_blockchain == 0 :
     change_blockchain      = -1
     price_from_blockchain  = -1
    else :
     change_blockchain      = ((weighted_external_price - price_from_blockchain)/price_from_blockchain)*100
    t.add_row([asset,
               1/weighted_external_price,
               1/mean_exchanges,
               1/median_exchanges,
               1/price_from_blockchain,
               change_my,
               change_blockchain,
               age+" ago" ])
 print("\n"+t.get_string())

## ----------------------------------------------------------------------------
## Asset rename world<->BTS
## ----------------------------------------------------------------------------
def bts_yahoo_map(asset) :
 if asset in _bts_yahoo_map:
  return _bts_yahoo_map[asset]
 else :
  return asset

## ----------------------------------------------------------------------------
## Run Script
## ----------------------------------------------------------------------------
if __name__ == "__main__":
 core_symbol = "BTS"
 _all_bts_assets = ["BTC", "SILVER", "GOLD", "TRY", "SGD", "HKD", "RUB", "SEK", "NZD",
                   "CNY", "MXN", "CAD", "CHF", "AUD", "GBP", "JPY", "EUR", "USD",
                   "KRW" ] # , "SHENZHEN", "HANGSENG", "NASDAQC", "NIKKEI"
 _bases =["CNY", "USD", "BTC", "EUR", "HKD", "JPY"]
 _yahoo_base  = ["USD","EUR","CNY","JPY","HKD"]
 _yahoo_quote = ["XAG", "XAU", "TRY", "SGD", "HKD", "RUB", "SEK", "NZD", "CNY",
                 "MXN", "CAD", "CHF", "AUD", "GBP", "JPY", "EUR", "USD", "KRW"]
 _yahoo_indices = {
 #                    "399106.SZ" : core_symbol,  #"CNY",  # SHENZHEN
 #                    "^HSI"      : core_symbol,  #"HKD",  # HANGSENG
 #                    "^IXIC"     : core_symbol,  #"USD",  # NASDAQC
 #                    "^N225"     : core_symbol   #"JPY"   # NIKKEI
                 }
 _bts_yahoo_map = {
      "XAU"       : "GOLD",
      "XAG"       : "SILVER",
      "399106.SZ" : "SHENZHEN",
      "000001.SS" : "SHANGHAI",
      "^HSI"      : "HANGSENG",
      "^IXIC"     : "NASDAQC",
      "^N225"     : "NIKKEI"
 }
 _request_headers = {'content-type': 'application/json',
                     'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}
 ## Call Parameters ###########################################################
 asset_list_publish = _all_bts_assets
 if len( sys.argv ) > 1 :
  if sys.argv[1] != "ALL":
   asset_list_publish = sys.argv
   asset_list_publish.pop(0)

 ## Initialization
 myWitness               = {}
 price_in_bts_weighted   = {}
 price_median_blockchain = {}
 assets                  = {}
 price                   = {}
 volume                  = {}
 lastUpdate              = {}
 myCurrentFeed           = {}

 for base in _bases  + [core_symbol]:
  price[base]            = {}
  volume[base]           = {}
  for asset in _all_bts_assets + [core_symbol]:
   price[base][asset]    = []
   volume[base][asset]   = []

 for asset in _all_bts_assets + [core_symbol]:
  price_in_bts_weighted[asset]   = 0.0
  price_median_blockchain[asset] = 0.0
  lastUpdate[asset]              = datetime.utcnow()
  myCurrentFeed[asset]           = {}

 ## rpc variables about bts rpc ###############################################
 rpc = GrapheneAPI(config.host, config.port, config.user, config.passwd)
 fetch_from_wallet(rpc)

 ## Get prices and stats ######################################################
 mythreads = {}
 mythreads["yahoo"]    = threading.Thread(target = fetch_from_yahoo)
 mythreads["yunbi"]    = threading.Thread(target = fetch_from_yunbi)
 mythreads["btc38"]    = threading.Thread(target = fetch_from_btc38)
 mythreads["bter"]     = threading.Thread(target = fetch_from_bter)
 mythreads["poloniex"] = threading.Thread(target = fetch_from_poloniex)
 mythreads["bittrex"]  = threading.Thread(target = fetch_from_bittrex)
 mythreads["btcavg"]   = threading.Thread(target = fetch_bitcoinaverage)

 print("[Starting Threads]: ", end="",flush=True)
 for t in mythreads :
  print("(%s)"%t, end="",flush=True)
  mythreads[t].start()
 for t in mythreads :
  mythreads[t].join() # Will wait for a thread until it finishes its task.
  print(".", end="",flush=True)

 ## Determine bts price ######################################################
 derive_prices()

 ## Only publish given feeds ##################################################
 asset_list_final = []
 for asset in asset_list_publish :
    if len(price[core_symbol][asset]) > 0 :
        if price_in_bts_weighted[asset] > 0.0:
            quote_precision = assets[asset]["precision"]
            base_precision  = assets["1.3.0"]["precision"] ## core asset
            core_price = price_in_bts_weighted[asset] * 10**(quote_precision-base_precision)
            core_price = fractions.Fraction.from_float(core_price).limit_denominator(100000)
            denominator = core_price.denominator
            numerator   = core_price.numerator

            assert assets[asset]["symbol"] is not asset

            price_feed = {
                      "settlement_price": {
                        "quote": {
                          "asset_id": "1.3.0",
                          "amount": denominator
                        },
                        "base": {
                          "asset_id": assets[asset]["id"],
                          "amount": numerator
                        }
                      },
                      "maintenance_collateral_ratio": config.maintenance_collateral_ratio,
                      "short_squeeze_ratio": config.short_squeeze_ratio,
                      "core_exchange_rate": {
                        "quote": {
                          "asset_id": assets[asset]["id"],
                          "amount": numerator
                        },
                        "base": {
                          "asset_id": "1.3.0",
                          "amount": int(denominator * config.core_exchange_factor)
                        }
                      }
                    }
            asset_list_final.append([ asset, price_feed ])

 ## Print some stats ##########################################################
 print_stats()

 ## Check publish rules and publich feeds #####################################
 if publish_rule() and rpc._confirm("Are you SURE you would like to publish this feed?") :
  print("Update required! Forcing now!")
  update_feed(rpc,asset_list_final)
 else :
  print("no update required")
