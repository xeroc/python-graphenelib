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

import json
import sys
import time
import statistics
import numpy as num
import sys
import fractions
from prettytable import PrettyTable
from math        import fabs
from pprint      import pprint
from datetime    import datetime
from grapheneapi import GrapheneAPI
import os.path

import threading
from multiprocessing.pool import ThreadPool
from concurrent import futures

## Only import config.py if config is not defined already
if 'config' not in globals():
    import config

debug = 0

## ----------------------------------------------------------------------------
## When do we have to force publish?
## ----------------------------------------------------------------------------
def publish_rule(rpc, asset):
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
 # REAL_PRICE = Lowest of external feeds                         = newPrice
 # MEDIAN = current median price according to the blockchain.    = price_median_blockchain[asset]
 ##############################################################################
 ## Define REAL_PRICE
 newPrice    = derived_prices[asset] #statistics.median( price[core_symbol][asset] )
 priceChange = fabs(price_median_blockchain[asset]-newPrice)/price_median_blockchain[asset] * 100.0

 ## Check max price change
 if priceChange > config.change_max :
      if not rpc._confirm("Price for asset %s has change from %f to %f (%f%%)! Do you want to continue?"%(
                            asset,price_median_blockchain[asset],newPrice,priceChange)) :
          return False # skip everything and return

 ## Rules
 if (datetime.utcnow()-lastUpdate[asset]).total_seconds() > config.maxAgeFeedInSeconds :
       print("Feeds for %s too old! Force updating!" % asset)
       return True
 elif newPrice     < price_median_blockchain[asset] and \
      price_median_blockchain[asset] > price_median_blockchain[asset]:
       print("External price move for %s: newPrice(%.8f) < feedmedian(%.8f) and newprice(%.8f) > feedmedian(%f) Force updating!"\
              % (asset,newPrice,price_median_blockchain[asset],newPrice,price_median_blockchain[asset]))
       return True
 elif priceChange > config.change_min and\
      (datetime.utcnow()-lastUpdate[asset]).total_seconds() > config.maxAgeFeedInSeconds > 20*60:
       print("New Feeds differs too much for %s %.8f > %.8f! Force updating!" \
              % (asset,fabs(price_median_blockchain[asset]-newPrice), config.change_min))
       return True

 return False

## ----------------------------------------------------------------------------
## Fetch data
## ----------------------------------------------------------------------------

## ----------------------------------------------------------------------------
## Fetch current feeds, assets and feeds of assets from wallet
## ----------------------------------------------------------------------------
def fetch_from_wallet(rpc):
 print("Fetching data from wallet...")
 ## Get my Witness
 global myWitness
 myWitness = rpc.get_witness(config.witness_name)
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
def update_feed(rpc, feeds):
 wallet_was_unlocked = False

 if rpc.is_locked() :
  wallet_was_unlocked = True
  print( "Unlocking wallet" )
  ret = rpc.unlock(config.unlock)

 print("constructing feed for witness %s"%config.witness_name)
 handle = rpc.begin_builder_transaction();
 for asset in feeds :
  if not feeds[asset]["publish"] : continue
  rpc.add_operation_to_builder_transaction(handle, 
        [19, {  # id 19 corresponds to price feed update operation
                "asset_id"  : feeds[asset]["asset_id"],
                "feed"      : feeds[asset]["feed"],
                "publisher" : myWitness["witness_account"],
             }])

 # Set fee
 rpc.set_fees_on_builder_transaction(handle, "1.3.0")

 # Signing and Broadcast
 signedTx = rpc.sign_builder_transaction(handle, True)
 print(json.dumps(signedTx,indent=4));

 if wallet_was_unlocked :
  print( "Relocking wallet" )
  rpc.lock()

## ----------------------------------------------------------------------------
## calculate feed prices in BTS for all assets given the exchange prices in USD,CNY,BTC,...
## ----------------------------------------------------------------------------
def derive_prices(feed):
 price_result = {}
 for asset in _all_bts_assets + [core_symbol]:
  price_result[asset]    = 0.0

 for asset in asset_list_publish :

  this_asset_config = config.asset_config[asset]    if asset in config.asset_config           else config.asset_config["default"]
  sources           = list(feed)                    if this_asset_config["sources"][0] == '*' else this_asset_config["sources"]
  price_metric      = this_asset_config["metric"]   if "metric" in this_asset_config          else config.asset_config["default"]["metric"]
  discount          = this_asset_config["discount"] if "discount" in this_asset_config        else config.asset_config["default"]["discount"]

  for base in _all_bts_assets  + [core_symbol]:
   price[base]            = {}
   volume[base]           = {}
   for quote in _all_bts_assets + [core_symbol]:
    price[base][quote]    = []
    volume[base][quote]   = []

  # Invert pairs
  for datasource in list(sources) : 
   if not feed[datasource] : continue
   for base in list(feed[datasource]) :
    for quote in list(feed[datasource][base]) :
     # Original price/volume
     price[base][quote].append(feed[datasource][base][quote]["price"])
     volume[base][quote].append(feed[datasource][base][quote]["volume"])

     if feed[datasource][base][quote]["price"] > 0 and \
        feed[datasource][base][quote]["volume"] > 0 :
      # Inverted pair price/volume
      price[quote][base].append((float(1.0/feed[datasource][base][quote]["price"] )))
      # volume is usually in "quote"
      volume[quote][base].append((float(feed[datasource][base][quote]["volume"]*feed[datasource][base][quote]["price"])))

  # derive BTS prices for all _base assets
  for base in _bases :
   for quote in _bases :
    if base == quote : continue
    for ratio in price[base][quote] :
     for idx in range(0, len(price[base][core_symbol])) :
      if volume[base][core_symbol][idx] == 0 : continue
      price[quote][core_symbol].append( (float(price[base][core_symbol][idx] /ratio)))
      volume[quote][core_symbol].append((float(volume[base][core_symbol][idx]/ratio)))

  for base in _bases :
   for quote in asset_list_publish :
    if base == quote : continue
    for ratio in price[base][quote] :
     for idx in range(0, len(price[base][core_symbol])) :
      if volume[base][core_symbol][idx] == 0 : continue
      price[core_symbol][quote].append( 1.0/(float(price[base][core_symbol][idx] /ratio)))
      volume[core_symbol][quote].append(1.0/(float(volume[base][core_symbol][idx]/ratio)))

  # Derive Final Price according to price metric
  if price_metric == "median" :
   price_result[asset] = statistics.median(price[core_symbol][asset])

  elif price_metric == "mean" :
   price_result[asset] = statistics.mean(price[core_symbol][asset])

  elif price_metric == "weighted" :
   assetvolume= [v for v in  volume[core_symbol][asset] ]
   assetprice = [p for p in  price[core_symbol][asset]  ]

   if len(assetvolume) > 1 :
    price_result[asset] = num.average(assetprice, weights=assetvolume)
   else :
    price_result[asset] = assetprice[0]

  else :
   raise Exception("Configuration error, 'price_metric' has to be out of [ 'median', 'mean', 'weighted]")

  # Discount and price convertion to "price for one BTS" i.e.  base=*, quote=core_symbol
  price_result[asset] = discount/(price_result[asset])

 return price_result

## ----------------------------------------------------------------------------
## Print stats as table
## ----------------------------------------------------------------------------
def print_stats(feeds) :
 t = PrettyTable(["asset","price for one BTS","mean exchanges","median exchanges","blockchain median","% change (my)","% change (net)","last update","publish"])
 t.align                   = 'r'
 t.border                  = True
 t.float_format['price for one BTS']     = ".8"
 t.float_format['mean exchanges']        = ".8"
 t.float_format['median exchanges']      = ".8"
 t.float_format['blockchain median']     = ".8"
 t.float_format['% change (my)']         = ".5"
 t.float_format['% change (net)']        = ".5"
 #t.align['BTC']            = "r"
 for asset in asset_list_publish :
    if len(price[core_symbol][asset]) < 1 : continue # empty asset
    age                     = (str(datetime.utcnow()-lastUpdate[asset]))
    weighted_external_price = derived_prices[asset]
    price_from_blockchain   = price_median_blockchain[asset]
    cur_feed                = float(myCurrentFeed[asset])
    ## Stats
    mean_exchanges          = statistics.mean(price[core_symbol][asset])
    median_exchanges        = statistics.median(price[core_symbol][asset])
    if cur_feed == 0 :               change_my              = -1
    else :                           change_my              = ((weighted_external_price - cur_feed)/cur_feed)*100
    if price_from_blockchain == 0 :
     change_blockchain      = -1
     price_from_blockchain  = -1
    else :
     change_blockchain      = ((weighted_external_price - price_from_blockchain)/price_from_blockchain)*100
    t.add_row([asset,
               1/weighted_external_price,
               mean_exchanges,
               median_exchanges,
               price_from_blockchain,
               change_my,
               change_blockchain,
               age+" ago",
               "X" if feeds[asset]["publish"] else ""
             ])
 print("\n"+t.get_string())

## ----------------------------------------------------------------------------
## Startup method
## ----------------------------------------------------------------------------
def update_price_feed() :
 global derived_prices

 for asset in _all_bts_assets + [core_symbol]:
  price_median_blockchain[asset] = 0.0
  lastUpdate[asset]              = datetime.utcnow()
  myCurrentFeed[asset]           = {}

 ## Get Prices from Feed Sources ##############################################
 if debug and os.path.isfile('data.json') : 
 ## Load data from disk for (faster) debugging
  with open('data.json', 'r') as fp:
     feed = json.load(fp)
 else : 
 ## Get prices from sources
  pool = futures.ThreadPoolExecutor(max_workers=8)
  feed      = {}
  mythreads = {}

  for name in config.feedSources :
   print("(%s)"%name, end="",flush=True)
   mythreads[name] = pool.submit( config.feedSources[name].fetch )

  for name in config.feedSources :
   print(".", end="",flush=True)
   feed[name]      = mythreads[name].result()

  with open('data.json', 'w') as fp:
     json.dump(feed, fp)

 ## Determine bts price ######################################################
 derived_prices = derive_prices(feed)

 ## rpc variables about bts rpc ###############################################
 rpc = GrapheneAPI(config.host, config.port, config.user, config.passwd)
 fetch_from_wallet(rpc)

 ## Only publish given feeds ##################################################
 price_feeds = {}
 update_required = False

 for asset in asset_list_publish :
    if len(price[core_symbol][asset]) > 0 :
        if derived_prices[asset] > 0.0:
            quote_precision = assets[asset]["precision"]
            symbol          = assets[asset]["symbol"]
            assert symbol is not asset

            base_precision  = assets["1.3.0"]["precision"] ## core asset
            core_price      = derived_prices[asset] * 10**(quote_precision-base_precision)
            core_price      = fractions.Fraction.from_float(core_price).limit_denominator(100000)
            denominator     = core_price.denominator
            numerator       = core_price.numerator


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
                      "maintenance_collateral_ratio" : 
                                config.asset_config[symbol]["maintenance_collateral_ratio"]
                                if (symbol in config.asset_config and "maintenance_collateral_ratio" in config.asset_config[symbol])
                                else config.asset_config["default"]["maintenance_collateral_ratio"],
                      "maximum_short_squeeze_ratio"  : 
                                config.asset_config[symbol]["maximum_short_squeeze_ratio"]
                                if (symbol in config.asset_config and "maximum_short_squeeze_ratio" in config.asset_config[symbol])
                                else config.asset_config["default"]["maximum_short_squeeze_ratio"],
                      "core_exchange_rate": {
                        "quote": {
                          "asset_id": "1.3.0",
                          "amount": int(denominator * (
                                        config.asset_config[symbol]["core_exchange_factor"]
                                        if (symbol in config.asset_config and "core_exchange_factor" in config.asset_config[symbol])
                                        else config.asset_config["default"]["core_exchange_factor"]
                                       ))
                        },
                        "base": {
                          "asset_id": assets[asset]["id"],
                          "amount": numerator
                        }
                      }
                    }

            asset_update_required = publish_rule(rpc,asset)
            if asset_update_required: update_required = True 
            price_feeds[symbol] = {
                                     "asset_id": assets[asset]["id"],
                                     "feed":     price_feed,
                                     "publish":  asset_update_required
                                  }

 ## Print some stats ##########################################################
 print_stats(price_feeds)

 ## Check publish rules and publich feeds #####################################

 if update_required :
  publish = False
  if config.ask_confirmation :
   if rpc._confirm("Are you SURE you would like to publish this feed?") :
    publish = True
  else :
    publish = True

  if publish :
    print("Update required! Forcing now!")
    update_feed(rpc,price_feeds)
 else :
  print("no update required")

## ----------------------------------------------------------------------------
## Initialize global variables
## ----------------------------------------------------------------------------
core_symbol = "BTS"
_all_bts_assets = ["BTC", "SILVER", "GOLD", "TRY", "SGD", "HKD", "NZD",
               "CNY", "MXN", "CAD", "CHF", "AUD", "GBP", "JPY", "EUR", "USD",
               "KRW" ] # , "SHENZHEN", "HANGSENG", "NASDAQC", "NIKKEI", "RUB", "SEK"
_bases =["CNY", "USD", "BTC", "EUR", "HKD", "JPY"]

## Call Parameters ###########################################################
asset_list_publish = _all_bts_assets
if len( sys.argv ) > 1 :
 if sys.argv[1] != "ALL":
  asset_list_publish = sys.argv
  asset_list_publish.pop(0)

## global variables initialization
myWitness               = {}
price_median_blockchain = {}
assets                  = {}
price                   = {}
volume                  = {}
lastUpdate              = {}
myCurrentFeed           = {}
derived_prices          = {}

if __name__ == "__main__":
 update_price_feed()
