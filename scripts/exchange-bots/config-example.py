from bot.strategies.maker import MakerRamp, MakerSellBuyWalls

wallet_host           = "localhost"
wallet_port           = 8092
wallet_user           = ""
wallet_password       = ""
witness_url           = "ws://testnet.bitshares.eu/ws"
witness_user          = ""
witness_password      = ""

watch_markets         = ["PEG.PARITY : TEST", "PEG.RANDOM : TEST"]
market_separator      = " : "

bots = {}

#############################
# Ramps
#############################
bots["MakerRexp"] = {"bot" : MakerRamp,
                     "markets" : ["PEG.PARITY : TEST"],
                     "target_price" : "feed",
                     "spread_percentage" : 0.2,
                     "volume_percentage" : 30,
                     "ramp_price_percentage" : 2,
                     "ramp_step_percentage" : 0.1,
                     "ramp_mode" : "linear"
                     }
bots["MakerRamp"] = {"bot" : MakerRamp,
                     "markets" : ["PEG.PARITY : TEST"],
                     "target_price" : "feed",
                     "spread_percentage" : 4,
                     "volume_percentage" : 30,
                     "ramp_price_percentage" : 4,
                     "ramp_step_percentage" : 0.5,
                     "ramp_mode" : "exponential"
                     }
#############################
# Walls
#############################
bots["MakerWall"] = {"bot" : MakerSellBuyWalls,
                     "markets" : ["PEG.PARITY : TEST"],
                     "target_price" : "feed",
                     "spread_percentage" : 5,
                     "volume_percentage" : 10,
                     "symmetric_sides" : True,
                     }
bots["MakerBridge"] = {"bot" : MakerSellBuyWalls,
                       "markets" : ["PEG.PARITY : TEST"],
                       "target_price" : 1.0,
                       "spread_percentage" : 90,
                       "volume_percentage" : 10,
                       "symmetric_sides" : True,
                       }


account               = "xeroc"
safe_mode = False
