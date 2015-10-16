################################################################################
## RPC-client connection information (required)
################################################################################
host   = "localhost"
port   = 8092
user   = ""
passwd = ""
unlock = ""

################################################################################
## Delegate Feed Publish Parameters
################################################################################
delegate_name            = "init0"
maxAgeFeedInSeconds      = 60*60 # 1hour

################################################################################
## Fine tuning
################################################################################
discount                 = 0.995
core_exchange_factor     = 1.05 # 5% surplus if paying fees in bitassets

minValidAssetPriceInBTC  = 0.00001
change_min               = 0.5

## Enable exchanges
enable_yunbi             = True
enable_btc38             = True
enable_bter              = False
enable_poloniex           = True
enable_bittrex           = True
enable_btcavg            = True

## trust level for exchanges (if an exception happens and level is 0.8 script
##                            will quit with a failure)
btc38_trust_level        = 0.9
bter_trust_level         = 0.5
poloniex_trust_level     = 1.0
bittrex_trust_level      = 0.5
yunbi_trust_level        = 0.8
