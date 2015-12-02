#!/usr/bin/env python3
# coding=utf8 sw=4 expandtab ft=python

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
import config

## ----------------------------------------------------------------------------
## When do we have to force publish?
## ----------------------------------------------------------------------------
def publish_rule(rpc, asset):
    if debug : return False

    this_asset_config = config.asset_config[asset]    if asset in config.asset_config           else config.asset_config["default"]
    price_metric      = this_asset_config["metric"]   if "metric" in this_asset_config          else config.asset_config["default"]["metric"]
    newPrice          = derived_prices[asset][price_metric]

    priceChange       = fabs(price_median_blockchain[asset]-newPrice)/price_median_blockchain[asset] * 100.0

    ## Check max price change
    if priceChange > config.change_max :
         if rpc._confirm("Price for asset %s has change from %f to %f (%f%%)! Do you want to continue?"%(
                               asset,price_median_blockchain[asset],newPrice,priceChange)) :
            return True

    ## Feed too old
    if (datetime.utcnow()-lastUpdate[asset]).total_seconds() > config.maxAgeFeedInSeconds :
          print("Feed for %s too old! Forcing update!" % asset)
          return True

    ## External Price movement
    if priceChange > config.change_min :
          print("New Feeds differs too much for %s %.8f > %.8f! Force updating!" \
                 % (asset,fabs(price_median_blockchain[asset]-newPrice), config.change_min))
          return True

    return False

## ----------------------------------------------------------------------------
## Fetch data
## ----------------------------------------------------------------------------

## ----------------------------------------------------------------------------
## Get last block
## ----------------------------------------------------------------------------
def get_last_block(rpc):
    return rpc.get_dynamic_global_properties()["head_block_number"]

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
    #print(json.dumps(signedTx,indent=4));

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

         for base in _all_bts_assets  + [core_symbol]:
             price[base]            = {}
             volume[base]           = {}
             for quote in _all_bts_assets + [core_symbol]:
                 price[base][quote]    = []
                 volume[base][quote]   = []

         # Load feed data into price/volume array for processing
         # This few lines solely take the data of the chosen exchanges and put
         # them into price[base][quote]. Since markets are symmetric, the
         # corresponding price[quote][base] is derived accordingly and the
         # corresponding volume is derived at spot price
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

         # derive BTS prices for all assets in asset_list_publish
         # This loop adds prices going via 2 markets:
         # E.g. : CNY:BTC -> BTC:BTS = CNY:BTS
         for targetasset in asset_list_publish :
             for base in _bases :
                 if base == targetasset : continue
                 for ratio in price[targetasset][base] :
                     for idx in range(0, len(price[base][core_symbol])) :
                         if volume[base][core_symbol][idx] == 0 : continue
                         price[targetasset][core_symbol].append( (float(price[base][core_symbol][idx]  * ratio)))
                         volume[targetasset][core_symbol].append((float(volume[base][core_symbol][idx] * ratio)))

         # Derive all prices and pick the right one later
         assetvolume= [v for v in  volume[asset][core_symbol] ]
         assetprice = [p for p in   price[asset][core_symbol]  ]
         price_median = statistics.median(price[asset][core_symbol])
         price_mean   = statistics.mean(price[asset][core_symbol])
         if len(assetvolume) > 1 :
             price_weighted = num.average(assetprice, weights=assetvolume)
         else :
             price_weighted = assetprice[0]

         # price convertion to "price for one BTS" i.e.  base=*, quote=core_symbol
         price_result[asset] = {
                                 "mean"    : price_mean,
                                 "median"  : price_median,
                                 "weighted": price_weighted,
                               }

     return price_result

## ----------------------------------------------------------------------------
## Print stats as table
## ----------------------------------------------------------------------------
def formatPercentageMinus(f) :
    return "\033[1;31m%+5.2f%%\033[1;m" % f
def formatPercentagePlus(f) :
    return "\033[1;32m%+5.2f%%\033[1;m" % f
def formatPrice(f) :
    return "\033[1;33m%.8f\033[1;m" %f
def priceChange(new,old):
    if float(old)==0.0: return -1
    else : 
        percent = ((float(new)-float(old))) / float(old) * 100
        if percent >= 0 :
            return formatPercentagePlus(percent)
        else :
            return formatPercentageMinus(percent)

def compare_feeds(blamePrices, newPrices) :
    t = PrettyTable(["asset","blame price","recalculated price","mean","median","weighted"])
    t.align                   = 'c'
    t.border                  = True
    #t.align['BTC']            = "r"
    for asset in asset_list_publish :
        # Get Final Price according to price metric
        this_asset_config = config.asset_config[asset]    if asset in config.asset_config           else config.asset_config["default"]
        price_metric      = this_asset_config["metric"]   if "metric" in this_asset_config          else config.asset_config["default"]["metric"]

        blamed_prices     = blamePrices[asset]
        new_prices        = newPrices[asset]
        blamed            = blamePrices[asset][price_metric]
        new               = newPrices[asset][price_metric]

        t.add_row([asset,
                   ("%s"% formatPrice(blamed)),
                   ("%s (%s)"% (formatPrice(new), priceChange(new, blamed))),
                   ("%s"% priceChange(new_prices["mean"],    blamed_prices["mean"])),
                   ("%s"% priceChange(new_prices["median"],  blamed_prices["median"])),
                   ("%s"% priceChange(new_prices["weighted"],blamed_prices["weighted"])),
                 ])
    print(t.get_string())

def print_stats(feeds) :
    t = PrettyTable(["asset","new price","mean","median","weighted","blockchain","my last price","last update","publish"])
    t.align                   = 'c'
    t.border                  = True
    #t.align['BTC']            = "r"
    for asset in asset_list_publish :
        # Get Final Price according to price metric
        this_asset_config = config.asset_config[asset]    if asset in config.asset_config           else config.asset_config["default"]
        price_metric      = this_asset_config["metric"]   if "metric" in this_asset_config          else config.asset_config["default"]["metric"]

        age                     = (str(datetime.utcnow()-lastUpdate[asset])) if not (lastUpdate[asset]==datetime.fromtimestamp(0)) else "infinity"

        myprice                 = derived_prices[asset][price_metric]
        prices                  = derived_prices[asset]
        blockchain              = price_median_blockchain[asset]
        last                    = float(myCurrentFeed[asset])

        t.add_row([asset,
                   ("%s"     % formatPrice(myprice)),
                   ("%s (%s)"%(formatPrice(prices["mean"]),     priceChange(myprice,prices["mean"]))),
                   ("%s (%s)"%(formatPrice(prices["median"]),   priceChange(myprice,prices["median"]))),
                   ("%s (%s)"%(formatPrice(prices["weighted"]), priceChange(myprice,prices["weighted"]))),
                   ("%s (%s)"%(formatPrice(blockchain),         priceChange(myprice,blockchain))),
                   ("%s (%s)"%(formatPrice(last),               priceChange(myprice,last))),
                   age + " ago",
                   "X" if feeds[asset]["publish"] else ""
                 ])
    print(t.get_string())

## ----------------------------------------------------------------------------
## Startup method
## ----------------------------------------------------------------------------
def update_price_feed() :
    global derived_prices, config
    state = {}

    for asset in _all_bts_assets + [core_symbol]:
        price_median_blockchain[asset] = 0.0
        lastUpdate[asset]              = datetime.utcnow()
        myCurrentFeed[asset]           = {}

    ## Load Feedsource data #####################################################
    if configFile.blame != "latest" :
        if os.path.isfile("blame/"+configFile.blame+'.json') : 
            ## Load data from disk for (faster) debugging and verification
            with open("blame/"+configFile.blame+'.json', 'r') as fp:
                state = json.load(fp)
                ## Load feed sources
                feed  = state["feed"]
                ## Load configuration from old state
                configStruct = state["config"]
                for key in configStruct :
                    ## Skip asset config
                    if key == "asset_config" : continue
                    config.__dict__[key] = configStruct[key]

        else :
            sys.exit("Configuration error: Either set 'blame' to an existing "+
                     "block number from the blame/ to verify or set it to "+
                     "'latest' to run the script online! ")
    else : 
        ## Load configuration from file
        config = configFile
        ## Get prices online from sources
        pool = futures.ThreadPoolExecutor(max_workers=8)
        feed      = {}
        mythreads = {}

        for name in config.feedSources :
            print("(%s)"%name, end="",flush=True)
            mythreads[name] = pool.submit( config.feedSources[name].fetch )

        for name in config.feedSources :
            print(".", end="",flush=True)
            feed[name]      = mythreads[name].result()

    ## Determine bts price ######################################################
    derived_prices = derive_prices(feed)

    ## rpc variables about bts rpc ##############################################
    rpc = GrapheneAPI(config.host, config.port, config.user, config.passwd)
    fetch_from_wallet(rpc)

    ## Only publish given feeds #################################################
    price_feeds = {}
    update_required = False

    for asset in asset_list_publish :
       # Get Final Price according to price metric
       this_asset_config = config.asset_config[asset]    if asset in config.asset_config           else config.asset_config["default"]
       price_metric      = this_asset_config["metric"]   if "metric" in this_asset_config          else config.asset_config["default"]["metric"]

       if derived_prices[asset][price_metric] > 0.0:
           quote_precision = assets[asset]["precision"]
           symbol          = assets[asset]["symbol"]
           assert symbol is not asset

           base_precision  = assets["1.3.0"]["precision"] ## core asset
           core_price      = derived_prices[asset][price_metric] * 10**(quote_precision-base_precision)
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

    if not debug :
        ## Print some stats ##########################################################
        print_stats(price_feeds)

        ## Verify results or store them ##############################################
        configStruct = {}
        for key in dir(config) :
            if key[0] == "_" : continue
            if key == "feedSources" : continue ## can't storage objects / TODO: pickle
            if key == "feedsources" : continue
            if key == "subprocess"  : continue
            configStruct[key] = config.__dict__[key]
        # Store State
        state["feed"]           = feed
        state["derived_prices"] = derived_prices
        state["price_feeds"]    = price_feeds
        state["lastblock"]      = get_last_block(rpc)
        state["config"]         = configStruct
        blameFile               = "blame/"+str(state["lastblock"])+'.json'
        with open(blameFile, 'w') as fp:
           json.dump(state, fp)
        print("Blamefile: "+blameFile)

        ## Check publish rules and publich feeds #####################################
        if update_required and not debug :
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

    else : 
        # Verify results
        print()
        print("[Warning] This script is loading old data for debugging. No price can be published.\n"+\
              "          Please set 'blame' to 'latest' if you are ready to go online!")
        print()
        compare_feeds(state["derived_prices"], derived_prices)


## ----------------------------------------------------------------------------
## Initialize global variables
## ----------------------------------------------------------------------------
configFile = config
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
debug                   = False if configFile.blame == "latest" else True

if __name__ == "__main__":
    update_price_feed()
