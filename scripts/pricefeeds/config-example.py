################################################################################
## RPC-client connection information (required)
################################################################################
host   = "localhost"
port   = 8092
user   = ""
passwd = ""
unlock = ""

ask_confirmation = True

################################################################################
## Delegate Feed Publish Parameters
################################################################################
delegate_name            = "init0"
maxAgeFeedInSeconds      = 60*60 # 1hour

################################################################################
## Fine tuning
################################################################################
discount                     = 0.995  # discoun for shorts
core_exchange_factor         = 0.95   # 5% discount if paying fees in bitassets
minValidAssetPriceInBTC      = 100 * 1e-8# minimum valid price for BTS in BTC
price_metric                 = "weighted" # "median", "mean", or "weighted" (by volume)
change_min                   = 0.5    # Percentage of price change to force an update
change_max                   = 5.0    # Percentage of price change to cause a warning

################################################################################
## Asset specific Borrow/Short parameters
################################################################################
# Call when collateral only pays off 175% the debt
default_maintenance_collateral_ratio = 1750
maintenance_collateral_ratio = {
                                  "USD" : 1750,
                               }


default_maximum_short_squeeze_ratio  = 1100   # Stop calling when collateral only pays off 110% of the debt
maximum_short_squeeze_ratio  = {
                                  "USD" : 1100,
                               }

################################################################################
## Enable exchanges
################################################################################
enable_bter              = False # No BTS2
enable_btc38             = False # No official statement for BTS2 yet
enable_yunbi             = False # currently halted
enable_poloniex          = True
enable_bittrex           = True
enable_btcavg            = True
enable_ccedk             = True
enable_btcid             = True

## trust level for exchanges (if an exception happens and level is 0.8 script
##                            will quit with a failure)
<<<<<<< HEAD
poloniex_trust_level     = 1.0 # trades BTS2
ccedk_trust_level        = 1.0 # trades BTS2
yunbi_trust_level        = 1.0
bittrex_trust_level      = 0.5 # is currently migrating

btc38_trust_level        = 0.0 # disabled!
btcid_trust_level        = 0.0 # disabled!
bter_trust_level         = 0.0 # disabled!
=======
poloniex_trust_level     = 1.0
ccedk_trust_level        = 1.0
bittrex_trust_level      = 0.1
btcid_trust_level        = 0.5
btc38_trust_level        = 0.5
# disabled!
yunbi_trust_level        = 0.0
bter_trust_level         = 0.0
>>>>>>> [Price Feed] asset specific SQP etc
