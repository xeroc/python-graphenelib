import feedsources
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
## Fine tuning
################################################################################
minValidAssetPriceInBTC      = 100 * 1e-8  # minimum valid price for BTS in BTC

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
                       "sources" : ["yahoo", 
                                    "ccedk", 
                                    "yunbi", 
                                    "btc38", 
                                    "poloniex", 
                                    "bittrex", 
                                    "btcavg", 
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
                       "sources" : ["poloniex",
                                    "bittrex",
                                    "ccedk",
                                    "bittrex",
                                   ],
                   },
                   ## Settings for CNY take popular chinese exchanges into
                   ## account that let people trade without fees.
                   ## Hence, the metric should be median, since the volume could
                   ## be easily manipulated
                   "CNY" : {
                       "metric" : "median",
                       "sources" : ["poloniex",
                                    "bittrex",
                                    "huobi",
                                    "btcchina",
                                    "okcoin",
                                   ]
                   }
               }

################################################################################
## Exchanges and settings
## 
## trust:        a multiplicative factor for the volume
## allowFailure: bool variable that will (if not set or set to False) exit the
##               script on error
################################################################################
feedSources = {}
feedSources["yahoo"]    = feedsources.Yahoo(trust=1.0)
feedSources["btcavg"]   = feedsources.BitcoinAverage(trust=1.0)

feedSources["poloniex"] = feedsources.Poloniex(trust=1.0)
feedSources["ccedk"]    = feedsources.Ccedk(trust=1.0)
feedSources["yunbi"]    = feedsources.Yunbi(trust=1.0, allowFailure=True)
feedSources["btcchina"] = feedsources.BtcChina(trust=1.0)
feedSources["huobi"]    = feedsources.Huobi(trust=1.0)
feedSources["okcoin"]   = feedsources.Okcoin(trust=1.0, allowFailure=True)

feedSources["bittrex"]  = feedsources.Bittrex(trust=0.5)

feedSources["btcid"]    = feedsources.BitcoinIndonesia(trust=0.0)
feedSources["btc38"]    = feedsources.Btc38(trust=0.0)
feedSources["bter"]     = feedsources.Bter(trust=0.0)

################################################################################
# Debug Mode! This loads old data and prevents the script for publishing any
# price feed!
################################################################################
debug = False # True or False
