#!/usr/bin/env python3

################################################################################
#
#                D E F A U L T    C O N F I G U R A T I O N
#
#   This configuration represents a working example. Prices published are very
#   close to what they "should be". However, every witness has to judge on his
#   own as to whether these settings fit his needs.
#
################################################################################

core_symbol = "BTS"

import subprocess
import os
import feedsources
feedsources.core_symbol = core_symbol

################################################################################
# RPC-client connection information (required)
################################################################################
host   = "localhost"     # machine that runs a cli-wallet with -H parameter
port   = 8092            # RPC port, e.g.`-H 127.0.0.1:8092`
user   = ""              # API user (optional)
passwd = ""              # API user passphrase (optional)
unlock = ""              # password to unlock the wallet if the cli-wallet is locked

################################################################################
# Script runtime parameters
################################################################################
ask_confirmation             = True  # if true, a manual confirmation is required

################################################################################
# Feed Producer Name
################################################################################
producer_name                = "init0"

################################################################################
# Publishing Criteria
################################################################################
#
# Publish price if any of these are valid:
#
#  1.) price feed is older than maxAgeFeedInSeconds
#  2.) price has moved from my last published price by more than change_min
#
# Do NOT publish if
#
#  * Price has moved more than 'change_max'
#     AND
#  * Manual confirmation is 'false'
#
# A feed becomes invalid if it is older than 24h. Hence, it should be force
# published once a day (e.g. every 12h) Note that the script should be run more
# frequently and publishes only those prices that fit the publishing criteria
maxAgeFeedInSeconds          = 12 * 60 * 60  # max age of 12h
change_min                   = 0.5       # Percentage of price change to force an update
change_max                   = 5.0       # Percentage of price change to cause a warning

################################################################################
# Asset specific Settings
################################################################################
_all_assets = ["BTC", "SILVER", "GOLD", "TRY", "SGD", "HKD", "NZD",
               "CNY", "MXN", "CAD", "CHF", "AUD", "GBP", "JPY", "EUR", "USD",
               "KRW", "TCNY"]  # "SHENZHEN", "HANGSENG", "NASDAQC", "NIKKEI", "RUB", "SEK"
_bases = ["CNY", "USD", "BTC", "EUR", "HKD", "JPY"]

asset_config = {"default" : {  # DEFAULT BEHAVIOR
                    #
                    # how to derive a single price from several sources
                    # Choose from: "median", "mean", or "weighted" (by volume)
                    "metric" : "weighted",
                    #
                    # Select sources for this particular asset. Each source
                    # has its own fetch() method and collects several markets
                    # any market of an exchanges is considered but only the
                    # current asset's price is derived
                    #
                    # Choose from: - "*": all,
                    #              - loaded exchanges (see below)
                    "sources" : [  # Required Exchanges for FIAT
                                 "btcavg",    # To get from BTC into USD/CNY/EUR
                                 "yahoo",     # To get from USD/CNY/EUR into other FIAT currencies
                                 # BTC/BTS exchanges (include BTC/* if available)
                                 "poloniex",
                                 "ccedk",
                                 "bittrex",
                                 "btc38",
                                 "yunbi",
                                 "bitshares",
                                 # ## BTC/* exchanges
                                 # "okcoin",   # no trading-fees
                                 # "btcchina", # no trading-fees
                                 # "huobi",    # no trading-fees
                                 ],
                    # Core exchange factor for paying transaction fees in
                    # non-BTS assets. This is a factor: 0.95 = 95%
                    "core_exchange_factor"          : 0.95,
                    # Call when collateral only pays off 175% the debt.
                    # This is denoted as: 1750 = 175% = 1.75
                    "maintenance_collateral_ratio"  : 1750,
                    # Stop calling when collateral only pays off 110% of the debt
                    # This is denoted as: 1100 = 110% = 1.10
                    "maximum_short_squeeze_ratio"   : 1100,
                    # If set to True, prices are also derived via 3
                    # markets instead of just two:
                    # E.g. : GOLD:USD -> USD:BTC -> BTC:BTS = GOLD:BTS
                    "derive_across_3markets" : False
                },
                # Exchanges trading BTC/BTS directly
                # (this does not include any other trading pairs)
                "BTC" : {
                    "metric" : "weighted",
                    "sources" : ["poloniex",
                                 "ccedk",
                                 "bittrex",
                                 "btc38",
                                 "yunbi",
                                 ],
                },
                # Settings for CNY take popular chinese exchanges into
                # account that let people trade without fees.
                # Hence, the metric should be median, since the volume could
                # be easily manipulated
                "CNY" : {
                    "metric" : "weighted",
                    "sources" : ["btc38",
                                 "yunbi",
                                 "huobi",
                                 "btcchina",
                                 "okcoin",
                                 ]
                },
                #
                # As requested by the issuer, the squeere ratio should be
                # 100.1%
                "TCNY" : {
                    "maximum_short_squeeze_ratio"   : 1001,
                },
                "TUSD" : {
                    "maximum_short_squeeze_ratio"   : 1001
                },
               }

# Other assets that are derived or something else.
# Currently available:
#
#    "sameas" : x     # uses the same asset price as a MPA above
#
# Note:
#  The usual asset specific parameters have to be set in "asset_config",
#  otherwise they will be ignored!
secondary_mpas = {"TCNY" : {"sameas" : "CNY"},
                  "TUSD" : {"sameas" : "USD"}
                  }

################################################################################
# Exchanges and settings
#
# scaleVolumeBy: a multiplicative factor for the volume
# allowFailure:  bool variable that will (if not set or set to False) exit the
#                script on error
################################################################################
feedSources = {}
feedSources["yahoo"]    = feedsources.Yahoo(scaleVolumeBy=1e7,
                                            quotes=["XAG", "XAU", "TRY", "SGD", "HKD", "NZD", "CNY", "MXN", "CAD", "CHF", "AUD", "GBP", "JPY", "EUR", "USD", "KRW"],
                                            quoteNames={"XAU"       : "GOLD",
                                                        "XAG"       : "SILVER",
                                                        # "399106.SZ" : "SHENZHEN",
                                                        # "000001.SS" : "SHANGHAI",
                                                        # "^HSI"      : "HANGSENG",
                                                        # "^IXIC"     : "NASDAQC",
                                                        # "^N225"     : "NIKKEI"
                                                        },
                                            bases=["USD", "EUR", "CNY", "JPY", "HKD"])
feedSources["btcavg"]   = feedsources.BitcoinAverage(quotes=["BTC"], bases=["USD", "EUR", "CNY"])

feedSources["poloniex"] = feedsources.Poloniex(allowFailure=True, quotes=["BTS"], bases=["BTC"])
feedSources["ccedk"]    = feedsources.Ccedk(allowFailure=True, quotes=["BTS"], bases=["BTC", "USD", "EUR", "CNY"])
feedSources["bittrex"]  = feedsources.Bittrex(allowFailure=True, quotes=["BTS"], bases=["BTC"])
feedSources["yunbi"]    = feedsources.Yunbi(allowFailure=True, quotes=["BTS", "BTC"], bases=["CNY"])
feedSources["btc38"]    = feedsources.Btc38(allowFailure=True, quotes=["BTS", "BTC"], bases=["BTC", "CNY"])

feedSources["bitshares"] = feedsources.Graphene(allowFailure=True,
                                                quotes=["BTS"],
                                                bases=["USD"],
                                                witness_url="wss://bitshares.openledger.info/ws",
                                                wallet_host=host,
                                                wallet_port=port)

feedSources["btcchina"] = feedsources.BtcChina(allowFailure=True, quotes=["BTC"], bases=["CNY"])
feedSources["okcoin"]   = feedsources.Okcoin(allowFailure=True, quotes=["BTC"], bases=["CNY", "USD"])
feedSources["huobi"]    = feedsources.Huobi(allowFailure=True, quotes=["BTC"], bases=["CNY"])

# feedSources["btcid"]    = feedsources.BitcoinIndonesia(allowFailure=True, quotes=["BTS"], bases=["BTC"])
# feedSources["bter"]     = feedsources.Bter(allowFailure=True, quotes=["BTC", "BTS"], bases=["BTC", "CNY", "USD"])

################################################################################
# Blame mode allows to verify old published prices
# All data requires is stored in the blame/ directoy. Filename is the head block
# number at the time of script execution.
# To recover a price (will not publish) simply set blame to the block number of
# an existing(!) file.
#
# Default: "latest"  # Will fetch prices from exchanges and publish it
################################################################################
blame = "latest"
# blame = "1428190"

################################################################################
# Git revision for storage in blame files
# (do not touch this line)
################################################################################
try :
    configPath = os.path.dirname(__file__)
    gittag = subprocess.check_output(["git", "-C", configPath, "rev-parse", "HEAD"]).decode("ascii").strip("\n")
except :
    pass

# coding=utf8 sw=4 expandtab ft=python
