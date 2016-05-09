#!/usr/bin/env python3
# coding=utf8 sw=4 ts=4 expandtab ft=python

"""######################  W  A  R  N  I  N  G   ###################################
##                                                                                ##
## This is EXPERIMENTAL code!!                                                    ##
##                                                                                ##
## If you are a feed producer capable of publishing a price feed for              ##
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
#################################################################################"""

import json
import sys
import statistics
import numpy as num
import fractions
from prettytable import PrettyTable
from math import fabs, sqrt
from datetime import datetime
from grapheneapi import GrapheneAPI
import os.path
from concurrent import futures
import config
from config import _all_assets, _bases, core_symbol


def publish_rule(rpc, asset):
    """ When do we have to force publish?
    """
    if debug :
        return False

    this_asset_config = config.asset_config[asset] if asset in config.asset_config else config.asset_config["default"]
    price_metric      = this_asset_config["metric"] if "metric" in this_asset_config else config.asset_config["default"]["metric"]
    newPrice          = derived_prices[asset][price_metric]
    oldPrice          = myCurrentFeed[asset]

    priceChange       = fabs(oldPrice - newPrice) / oldPrice * 100.0

    # Check max price change
    if abs(priceChange) > fabs(config.change_max) and lastUpdate[asset].timestamp() != 0.0 :
        if rpc._confirm("Price for asset %s has change from %f to %f (%f%%)! Do you want to continue?" % (
                        asset, oldPrice, newPrice, priceChange)) :
            return True
        else :
            return False

    # Feed too old
    if (datetime.utcnow() - lastUpdate[asset]).total_seconds() > config.maxAgeFeedInSeconds :
        print("Feed for %s too old! Forcing update!" % asset)
        return True

    # External Price movement
    if priceChange > config.change_min :
        print("%s: New Feeds differs too much: %.8f%% > %.8f%%! Force updating!" %
              (asset, priceChange, config.change_min))
        return True

    return False


def weighted_std(values, weights):
    """ Weighted std for statistical reasons
    """
    average = num.average(values, weights=weights)
    variance = num.average((values - average) ** 2, weights=weights)  # Fast and numerically precise
    return sqrt(variance)


def get_last_block(rpc):
    """ Get last block
    """
    return rpc.get_dynamic_global_properties()["head_block_number"]


def fetch_from_wallet(rpc):
    """ Fetch current feeds, assets and feeds of assets from wallet
    """
    print("Fetching data from wallet...")

    # Get feed producer
    global myWitness, producerAccount
    try:
        # try if witness name is actually a witness:
        myWitness = rpc.get_witness(config.producer_name)
        producerID = myWitness["witness_account"]
        producerAccount = rpc.get_account(producerID)
    except:
        producerAccount = rpc.get_account(config.producer_name)
        producerID = producerAccount["id"]
        pass

    # asset definition - mainly for precision
    for asset in asset_list_publish + ["1.3.0"]:
        a = rpc.get_asset(asset)
        assets[asset] = a  # resolve SYMBOL
        assets[a["id"]] = a  # resolve id

    # sorted list with settlement price with bts as quote first
    result_list_publish_sorted = []
    for asset in asset_list_publish :
        # feeds for asset
        result = rpc.get_bitasset_data(asset)
        if result['current_feed']['settlement_price']['quote']['asset_id'] == "1.3.0":
            result_list_publish_sorted.insert(0, result)
        else:
            result_list_publish_sorted.append(result)

    for result in result_list_publish_sorted:
        asset_id = result["current_feed"]["core_exchange_rate"]["base"]["asset_id"]
        asset = assets[asset_id]["symbol"]
        # defaults
        price_median_blockchain[asset] = 0.0
        myCurrentFeed[asset] = -1.0
        lastUpdate[asset] = datetime.fromtimestamp(0)

        try :
            # get current feed data
            base  = result["current_feed"]["settlement_price"]["base"]
            quote = result["current_feed"]["settlement_price"]["quote"]
            assert base is not "1.3.0"
            base_precision  = assets[base["asset_id"]]["precision"]
            quote_precision = assets[quote["asset_id"]]["precision"]
            base_price  = (int(base["amount"]) / 10 ** base_precision)
            quote_price = (int(quote["amount"]) / 10 ** quote_precision)

            quote_asset_id = result['current_feed']['settlement_price']['quote']['asset_id']
            quote_asset = assets[quote_asset_id]["symbol"]
            if quote_asset == "BTS":
                price_median_blockchain[asset] = float(base_price / quote_price)
            else:
                price_median_blockchain[asset] = float(base_price / quote_price) * price_median_blockchain[quote_asset]
            # (base should be 1.3.0)BTS) hence price is x USD/BTS)

            # my feed specifics
            for feed in result["feeds"] :
                if feed[0] == producerID :
                    lastUpdate[asset] = datetime.strptime(feed[1][0], "%Y-%m-%dT%H:%M:%S")
                    base  = feed[1][1]["settlement_price"]["base"]
                    quote = feed[1][1]["settlement_price"]["quote"]
                    assert base is not "1.3.0"
                    base_price  = (int(base["amount"]) / 10 ** base_precision)
                    quote_price = (int(quote["amount"]) / 10 ** quote_precision)
                    myCurrentFeed[asset] = float(base_price / quote_price)
                    break
        except ZeroDivisionError :
            print("No price feeds for asset %s available on the blockchain, yet!" % asset)


def update_feed(rpc, feeds):
    """ Send the new feeds!
    """
    wallet_was_unlocked = False

    if rpc.is_locked() :
        wallet_was_unlocked = True
        print("Unlocking wallet")
        rpc.unlock(config.unlock)

    print("constructing feed for producer %s" % config.producer_name)
    handle = rpc.begin_builder_transaction()
    for asset in feeds :
        if not feeds[asset]["publish"] :
            continue
        op = [19,  # id 19 corresponds to price feed update operation
              {"asset_id"  : feeds[asset]["asset_id"],
               "feed"      : feeds[asset]["feed"],
               "publisher" : producerAccount["id"],
               }]
        rpc.add_operation_to_builder_transaction(handle, op)

    # Set fee
    rpc.set_fees_on_builder_transaction(handle, "1.3.0")

    # Signing and Broadcast
    rpc.sign_builder_transaction(handle, True)

    if wallet_was_unlocked :
        print("Relocking wallet")
        rpc.lock()


def derive_prices(feed):
    """ calculate feed prices in BTS for all assets given the exchange prices in USD,CNY,BTC,...
    """
    price_result = {}
    for asset in _all_assets + [core_symbol]:
        price_result[asset]    = {}

    # secondary assets requirements
    secondaries = []
    for asset in config.secondary_mpas.keys():
        if "sameas" in config.secondary_mpas[asset]:
            secondaries.append(config.secondary_mpas[asset]["sameas"])

    for asset in asset_list_publish + secondaries:
        # secondary markets are different
        if asset in list(config.secondary_mpas.keys()) :
            continue

        this_asset_config = config.asset_config[asset] if asset in config.asset_config else config.asset_config["default"]
        sources           = list(feed) if this_asset_config["sources"][0] == '*' else this_asset_config["sources"]

        # Reset prices
        price = {}
        volume = {}
        for base in _all_assets  + [core_symbol]:
            price[base]            = {}
            volume[base]           = {}
            for quote in _all_assets + [core_symbol]:
                price[base][quote]    = []
                volume[base][quote]   = []

        # Load feed data into price/volume array for processing
        # This few lines solely take the data of the chosen exchanges and put
        # them into price[base][quote]. Since markets are symmetric, the
        # corresponding price[quote][base] is derived accordingly and the
        # corresponding volume is derived at spot price
        for datasource in list(sources) :
            if not feed[datasource] :
                continue
            for base in list(feed[datasource]) :
                if base == "response" :  # skip entries that store debug data
                    continue
                for quote in list(feed[datasource][base]) :
                    if quote == "response" :  # skip entries that store debug data
                        continue
                    if not base or not quote:
                        continue
                    # Skip markets with zero trades in the last 24h
                    if feed[datasource][base][quote]["volume"] == 0.0:
                        # print("Skipping %s's %s:%s market due to 0 volume in the last 24h" % (datasource, base, quote))
                        continue

                    # Original price/volume
                    price[base][quote].append(feed[datasource][base][quote]["price"])
                    volume[base][quote].append(feed[datasource][base][quote]["volume"])

                    if feed[datasource][base][quote]["price"] > 0 and \
                       feed[datasource][base][quote]["volume"] > 0 :
                        # Inverted pair price/volume
                        price[quote][base].append((float(1.0 / feed[datasource][base][quote]["price"])))
                        # volume is usually in "quote"
                        volume[quote][base].append((float(feed[datasource][base][quote]["volume"] * feed[datasource][base][quote]["price"])))

        # derive BTS prices for all assets in asset_list_publish
        # This loop adds prices going via 2 markets:
        # E.g. : CNY:BTC -> BTC:BTS = CNY:BTS
        # I.e. : BTS : interasset -> interasset : targetasset
        for interasset in _bases :
            if interasset == asset :
                continue
            for ratio in price[asset][interasset] :
                for idx in range(0, len(price[interasset][core_symbol])) :
                    if volume[interasset][core_symbol][idx] == 0 :
                        continue
                    price[asset][core_symbol].append((float(price[interasset][core_symbol][idx] * ratio)))
                    volume[asset][core_symbol].append((float(volume[interasset][core_symbol][idx] * ratio)))

        # derive BTS prices for all assets in asset_list_publish
        # This loop adds prices going via 3 markets:
        # E.g. : GOLD:USD -> USD:BTC -> BTC:BTS = GOLD:BTS
        # I.e. : BTS : interassetA -> interassetA : interassetB -> asset : interassetB
        if "derive_across_3markets" in this_asset_config and this_asset_config["derive_across_3markets"] :
            for interassetA in _bases :
                for interassetB in _bases :
                    if interassetB == asset :
                        continue
                    if interassetA == asset :
                        continue
                    if interassetA == interassetB :
                        continue

                    for ratioA in price[interassetB][interassetA] :
                        for ratioB in price[asset][interassetB] :
                            for idx in range(0, len(price[interassetA][core_symbol])) :
                                if volume[interassetA][core_symbol][idx] == 0 :
                                    continue
                                price[asset][core_symbol].append((float(price[interassetA][core_symbol][idx] * ratioA * ratioB)))
                                volume[asset][core_symbol].append((float(volume[interassetA][core_symbol][idx] * ratioA * ratioB)))

        # Derive all prices and pick the right one later
        assetvolume = [v for v in volume[asset][core_symbol]]
        assetprice  = [p for p in price[asset][core_symbol]]

        if len(assetvolume) > 1 :
            price_median = statistics.median(price[asset][core_symbol])
            price_mean   = statistics.mean(price[asset][core_symbol])
            price_weighted = num.average(assetprice, weights=assetvolume)
            price_std      = weighted_std(assetprice, assetvolume)
            if price_std > 0.1 :
                print("Asset %s shows high variance in fetched prices!" % (asset))
        elif len(assetvolume) == 1:
            price_median   = assetprice[0]
            price_mean     = assetprice[0]
            price_weighted = assetprice[0]
            price_std      = 0
            print("[Warning] Only a single source for the %s price could be identified" % asset)
        else :
            print("[Warning] No market route found for %s. Skipping price" % asset)
            continue

        # price convertion to "price for one BTS" i.e.  base=*, quote=core_symbol
        price_result[asset] = {"mean"    : price_mean,
                               "median"  : price_median,
                               "weighted": price_weighted,
                               "std"     : price_std * 100,  # percentage
                               "number"  : len(assetprice)}

    # secondary market pegged assets
    for asset in list(config.secondary_mpas.keys()) :
        if "sameas" in config.secondary_mpas[asset] :
            price_result[asset] = price_result[config.secondary_mpas[asset]["sameas"]]

    return price_result


def formatPercentageMinus(f) :
    return "\033[1;31m%+5.2f%%\033[1;m" % f


def formatPercentagePlus(f) :
    return "\033[1;32m%+5.2f%%\033[1;m" % f


def formatPrice(f) :
    return "\033[1;33m%.8f\033[1;m" % f


def formatStd(f) :
    if f > 5 :
        return "\033[1;31m%5.2f%%\033[1;m" % f
    else :
        return "\033[1;32m%5.2f%%\033[1;m" % f


def priceChange(new, old):
    if float(old) == 0.0:
        return -1
    else :
        percent = ((float(new) - float(old))) / float(old) * 100
        if percent >= 0 :
            return formatPercentagePlus(percent)
        else :
            return formatPercentageMinus(percent)


def compare_feeds(blamePrices, newPrices) :
    t = PrettyTable(["asset", "blame price",
                     "recalculated price", "mean",
                     "median", "wgt. avg.",
                     "wgt. std (#)"])
    t.align                   = 'c'
    t.border                  = True
    for asset in asset_list_publish :
        # Get Final Price according to price metric
        this_asset_config = config.asset_config[asset] if asset in config.asset_config else config.asset_config["default"]
        price_metric      = this_asset_config["metric"] if "metric" in this_asset_config else config.asset_config["default"]["metric"]

        if asset not in blamePrices :
            continue
        if asset not in newPrices :
            continue
        blamed_prices     = blamePrices[asset]
        new_prices        = newPrices[asset]
        blamed            = blamePrices[asset][price_metric]
        new               = newPrices[asset][price_metric]

        t.add_row([asset,
                   ("%s" % formatPrice(blamed)),
                   ("%s (%s)" % (formatPrice(new), priceChange(new, blamed))),
                   ("%s" % priceChange(new_prices["mean"], blamed_prices["mean"])),
                   ("%s" % priceChange(new_prices["median"], blamed_prices["median"])),
                   ("%s" % priceChange(new_prices["weighted"], blamed_prices["weighted"])),
                   ("%s (%2d)" % (formatStd(new_prices["std"]), new_prices["number"]))
                   ])
    print(t.get_string())


def print_stats(feeds) :
    t = PrettyTable(["asset", "new price", "mean",
                     "median", "wgt. avg.",
                     "wgt. std (#)", "blockchain",
                     "my last price", "last update",
                     "publish"])
    t.align                   = 'c'
    t.border                  = True
    for asset in feeds :
        # Get Final Price according to price metric
        this_asset_config = config.asset_config[asset] if asset in config.asset_config else config.asset_config["default"]
        price_metric      = this_asset_config["metric"] if "metric" in this_asset_config else config.asset_config["default"]["metric"]
        if asset not in derived_prices or price_metric not in derived_prices[asset] :
            continue

        age                     = (str(datetime.utcnow() - lastUpdate[asset])) if not (lastUpdate[asset] == datetime.fromtimestamp(0)) else "infinity"
        myprice                 = derived_prices[asset][price_metric]
        prices                  = derived_prices[asset]
        blockchain              = price_median_blockchain[asset]
        last                    = float(myCurrentFeed[asset])

        t.add_row([asset,
                   ("%s"       % formatPrice(myprice)),
                   ("%s (%s)"  % (formatPrice(prices["mean"]), priceChange(myprice, prices["mean"]))),
                   ("%s (%s)"  % (formatPrice(prices["median"]), priceChange(myprice, prices["median"]))),
                   ("%s (%s)"  % (formatPrice(prices["weighted"]), priceChange(myprice, prices["weighted"]))),
                   ("%s (%2d)" % (formatStd(prices["std"]), prices["number"])),
                   ("%s (%s)"  % (formatPrice(blockchain), priceChange(myprice, blockchain))),
                   ("%s (%s)"  % (formatPrice(last), priceChange(myprice, last))),
                   age + " ago",
                   "X" if feeds[asset]["publish"] else ""
                   ])
    print(t.get_string())


def update_price_feed() :
    global derived_prices, config
    state = {}

    for asset in _all_assets + [core_symbol]:
        price_median_blockchain[asset] = 0.0
        lastUpdate[asset]              = datetime.utcnow()
        myCurrentFeed[asset]           = {}

    if configFile.blame != "latest" :
        blameFile = config.configPath + "/blame/" + configFile.blame + ".json"
        if os.path.isfile(blameFile) :
            # Load data from disk for (faster) debugging and verification
            with open(blameFile, 'r') as fp:
                state = json.load(fp)
                # Load feed sources
                feed  = state["feed"]
                # Load configuration from old state
                configStruct = state["config"]
                for key in configStruct :
                    # Skip asset config
                    if key == "asset_config" :
                        continue
                    config.__dict__[key] = configStruct[key]

        else :
            sys.exit("Configuration error: Either set 'blame' to an existing " +
                     "block number from the blame/ to verify or set it to " +
                     "'latest' to run the script online! ")
    else :
        # Load configuration from file
        config = configFile
        # Get prices online from sources
        pool = futures.ThreadPoolExecutor(max_workers=8)
        feed      = {}
        mythreads = {}

        for name in config.feedSources :
            print("(%s)" % name, end="", flush=True)
            mythreads[name] = pool.submit(config.feedSources[name].fetch)

        for name in config.feedSources :
            print(".", end="", flush=True)
            feed[name] = mythreads[name].result()

    # Determine bts price ######################################################
    derived_prices = derive_prices(feed)

    # rpc variables about bts rpc ##############################################
    rpc = GrapheneAPI(config.host, config.port, config.user, config.passwd)
    fetch_from_wallet(rpc)

    # Only publish given feeds #################################################
    price_feeds = {}
    update_required = False

    for asset in asset_list_publish :

        # Get Final Price according to price metric
        this_asset_config = config.asset_config[asset] if asset in config.asset_config else config.asset_config["default"]
        price_metric      = this_asset_config["metric"] if "metric" in this_asset_config else config.asset_config["default"]["metric"]

        if asset not in derived_prices or price_metric not in derived_prices[asset] :
            print("Warning: Asset %s has no derived price!" % asset)
            continue
        if float(derived_prices[asset][price_metric]) > 0.0:
            quote_precision = assets[asset]["precision"]
            symbol          = assets[asset]["symbol"]
            assert symbol is not asset

            base_precision  = assets["1.3.0"]["precision"]  # core asset
            core_price      = derived_prices[asset][price_metric] * 10 ** (quote_precision - base_precision)
            core_price      = fractions.Fraction.from_float(core_price).limit_denominator(100000)
            denominator     = core_price.denominator
            numerator       = core_price.numerator

            price_feed = {"settlement_price": {
                          "quote": {"asset_id": "1.3.0",
                                    "amount": denominator
                                    },
                          "base": {"asset_id": assets[asset]["id"],
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
                          "quote": {"asset_id": "1.3.0",
                                    "amount": int(denominator * (
                                        config.asset_config[symbol]["core_exchange_factor"]
                                        if (symbol in config.asset_config and "core_exchange_factor" in config.asset_config[symbol])
                                        else config.asset_config["default"]["core_exchange_factor"]))
                                    },
                          "base": {"asset_id": assets[asset]["id"],
                                   "amount": numerator
                                   }}}

            asset_update_required = publish_rule(rpc, asset)
            if asset_update_required :
                update_required = True
            price_feeds[symbol] = {"asset_id": assets[asset]["id"],
                                   "feed":     price_feed,
                                   "publish":  asset_update_required
                                   }
        else :
            print("Warning: Asset %s has a negative derived price of %f (%s metric)!" % (asset, float(derived_prices[asset][price_metric]), price_metric))
            continue

    if not debug :
        # Print some stats ##########################################################
        print_stats(price_feeds)

        # Verify results or store them ##############################################
        configStruct = {}
        for key in dir(config) :
            if key[0] == "_" :
                continue
            if key == "feedSources" :
                continue
            if key == "feedsources" :
                continue
            if key == "subprocess"  :
                continue
            if key == "os"          :
                continue
            configStruct[key] = config.__dict__[key]
        # Store State
        state["feed"]           = feed
        state["derived_prices"] = derived_prices
        state["price_feeds"]    = price_feeds
        state["lastblock"]      = get_last_block(rpc)
        state["config"]         = configStruct
        blameFile               = config.configPath + "/blame/" + str(state["lastblock"]) + ".json"
        with open(blameFile, 'w') as fp:
            json.dump(state, fp)
        print("Blamefile: " + blameFile)

        # Check publish rules and publich feeds #####################################
        if update_required and not debug :
            publish = False
            if config.ask_confirmation :
                if rpc._confirm("Are you SURE you would like to publish this feed?") :
                    publish = True
            else :
                publish = True

            if publish :
                print("Update required! Forcing now!")
                update_feed(rpc, price_feeds)
        else :
            print("no update required")

    else :
        # Verify results
        print()
        print("[Warning] This script is loading old data for debugging. No price can be published.\n" +
              "          Please set 'blame' to 'latest' if you are ready to go online!")
        print()
        compare_feeds(state["derived_prices"], derived_prices)


# ----------------------------------------------------------------------------
# Initialize global variables
# ----------------------------------------------------------------------------
configFile = config

# Call Parameters ###########################################################
asset_list_publish = _all_assets
if len(sys.argv) > 1 :
    if sys.argv[1] != "ALL":
        asset_list_publish = sys.argv
        asset_list_publish.pop(0)

# global variables initialization
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
