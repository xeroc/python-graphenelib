#!/usr/bin/env python3
# coding=utf8 sw=4 expandtab ft=python
import feedsources
import subprocess

################################################################################
## RPC-client connection information (required)
################################################################################
host   = "localhost"     # machine that runs a cli-wallet with -H parameter
port   = 8092            # RPC port, e.g.`-H 127.0.0.1:8092`
user   = ""              # API user (optional)
passwd = ""              # API user passphrase (optional)
unlock = ""              # password to unlock the wallet if the cli-wallet is locked

################################################################################
## Script runtime parameters
################################################################################
ask_confirmation             = True # if true, a manual confirmation is required

################################################################################
## Witness Feed Publish Parameters
################################################################################
witness_name                 = "init0"
maxAgeFeedInSeconds          = 60*60  # A feed should be at most 1hour old
change_min                   = 0.5    # Percentage of price change to force an update
change_max                   = 5.0    # Percentage of price change to cause a warning

################################################################################
## Asset specific Settings
################################################################################
asset_config = {
                   "default" : { ## DEFAULT BEHAVIOR
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
                       "sources" : [
                                    ## Required Exchanges for FIAT
                                    "btcavg",    # To get from BTC into USD/CNY/EUR
                                    "yahoo",     # To get from USD/CNY/EUR into other FIAT currencies
                                    ## BTC/BTS exchanges (include BTC/* if available)
                                    "ccedk",
                                    "yunbi",
                                    "btc38",
                                    "poloniex", 
                                    "bittrex", 
                                    ## BTC/* exchanges
                                    #"okcoin",   # no trading-fees
                                    #"btcchina", # no trading-fees
                                    #"huobi",    # no trading-fees
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
                       # Multiplicative factor for discount when borrowing
                       # bitassets. This is a factor: 0.95 = 95%. 1.0 disables
                       # the discount
                       "discount"                      : 1.0,
                   },
                   ## Exchanges trading BTC/BTS directly
                   ## (this does not include any other trading pairs)
                   "BTC" : {
                       "metric" : "median",
                       "sources" : ["*"], ## All exchanges
                   },
                   ## Settings for CNY take popular chinese exchanges into
                   ## account that let people trade without fees.
                   ## Hence, the metric should be median, since the volume could
                   ## be easily manipulated
                   "CNY" : {
                       "metric" : "weighted",
                       "sources" : ["poloniex",
                                    "bittrex",
                                    "huobi",
                                    "btcchina",
                                    "okcoin",
                                    "btc38",
                                   ]
                   }
               }

################################################################################
## Exchanges and settings
## 
## scaleVolumeBy: a multiplicative factor for the volume
## allowFailure:  bool variable that will (if not set or set to False) exit the
##                script on error
################################################################################
feedSources = {}
feedSources["yahoo"]    = feedsources.Yahoo()
feedSources["btcavg"]   = feedsources.BitcoinAverage()

feedSources["poloniex"] = feedsources.Poloniex()
feedSources["ccedk"]    = feedsources.Ccedk()
feedSources["bittrex"]  = feedsources.Bittrex()
feedSources["btcchina"] = feedsources.BtcChina()
feedSources["huobi"]    = feedsources.Huobi()

feedSources["yunbi"]    = feedsources.Yunbi(allowFailure=True)
feedSources["okcoin"]   = feedsources.Okcoin(allowFailure=True)
feedSources["btc38"]    = feedsources.Btc38(allowFailure=True)

#feedSources["btcid"]    = feedsources.BitcoinIndonesia()
#feedSources["bter"]     = feedsources.Bter()

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
#blame = "1428190"

################################################################################
## Git revision for storage in blame files
## (do not touch this line)
################################################################################
gittag = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("ascii").strip("\n")
