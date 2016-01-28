# Wallet RPC connection details
wallet_host           = "localhost"
wallet_port           = 8092
wallet_user           = ""
wallet_password       = ""

# Websocket URL
witness_url           = "ws://testnet.bitshares.eu/ws"

# Set of ALL markets that you inted to serve
watch_markets         = ["PEG.PARITY : TEST"]
market_separator      = " : "  # separator between assets

# Your account that executes the trades
account               = "xeroc"

# If this flag is set to True, nothing will be done really
safe_mode             = True

# The Bots:

# Load the strategies
from strategies.maker import MakerRamp, MakerSellBuyWalls

# Each bot has its individual name and carries the strategy and settings
bots = {}

#############################
# MakerSellBuyWalls
#############################
bots["MakerWall"] = {"bot" : MakerSellBuyWalls,
                     # markets to serve
                     "markets" : ["PEG.PARITY : TEST"],
                     # target_price to place Ramps around (floating number or "feed")
                     "target_price" : "feed",
                     # +-percentage offset from target_price
                     "target_price_offset_percentage" : 5,
                     # allowed spread, your lowest orders will be placed here
                     "spread_percentage" : 5,
                     # The amount of funds (%) you want to use
                     "volume_percentage" : 10,
                     # Place symmetric walls on both sides?
                     "symmetric_sides" : True,
                     # Serve only on of both sides
                     "only_buy" : False,
                     "only_sell" : False,
                     }

##############################
# MakerRamp
##############################
bots["MakerRexp"] = {"bot" : MakerRamp,
                     # markets to serve
                     "markets" : ["PEG.PARITY : TEST"],
                     # target_price to place Ramps around (floating number or "feed")
                     "target_price" : "feed",
                     # +-percentage offset from target_price
                     "target_price_offset_percentage" : 5,
                     # allowed spread, your lowest orders will be placed here
                     "spread_percentage" : 0.2,
                     # The amount of funds (%) you want to use
                     "volume_percentage" : 30,
                     # Ramp goes up with volume up to a price increase of x%
                     "ramp_price_percentage" : 2,
                     # from spread/2 to ramp_price, place an order every x%
                     "ramp_step_percentage" : 0.3,
                     # "linear" ramp (equal amounts) or "exponential"
                     # (linearily increasing amounts)
                     "ramp_mode" : "linear",
                     # Serve only on of both sides
                     "only_buy" : False,
                     "only_sell" : False,
                     }
