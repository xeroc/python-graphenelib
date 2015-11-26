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
discount                     = 0.995       # discount for borrowing of an asset
minValidAssetPriceInBTC      = 100 * 1e-8  # minimum valid price for BTS in BTC
price_metric                 = "weighted"  # "median", "mean", or "weighted" (by volume)

################################################################################
## Asset specific Borrow/Short parameters
################################################################################
# Core exchange rate for paying transaction fees in non-BTS assets
core_exchange_factor = {
                                  "default" : 0.95, # default value
                                  "USD"     : 0.95, # asset-specific overwrite
                       }

# Call when collateral only pays off 175% the debt
maintenance_collateral_ratio = {
                                  "default" : 1750, # default value
                                  "USD"     : 1750, # asset-specific overwrite
                               }

# Stop calling when collateral only pays off 110% of the debt
maximum_short_squeeze_ratio  = {
                                  "default" : 1100, # default value
                                  "USD"     : 1100, # asset-specific overwrite
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
poloniex_trust_level     = 1.0 # trades BTS2
ccedk_trust_level        = 1.0 # trades BTS2
yunbi_trust_level        = 1.0
bittrex_trust_level      = 0.5 # is currently migrating

btc38_trust_level        = 0.0 # disabled!
btcid_trust_level        = 0.0 # disabled!
bter_trust_level         = 0.0 # disabled!
