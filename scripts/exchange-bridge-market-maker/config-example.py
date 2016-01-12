#: Connection Settings for the Wallet
wallet_host           = "localhost"
wallet_port           = 8092
wallet_user           = ""
wallet_password       = ""

#: Connection Settings for the Witness node
witness_url           = "ws://bitshares.openledger.info/ws"
witness_user          = ""
witness_password      = ""

#: Markets that are of interest for us
watch_markets         = ["BTC : TRADE.BTC",
                         "BTC : OPENBTC",
                         "OPENBTC : TRADE.BTC",
                         "OPENDASH : TRADE.DASH",
                         "OPENDOGE : TRADE.DOGE",
                         "OPENLTC : TRADE.LTC",
                         "OPENMUSE : TRADE.MUSE",
                         "OPENNBT : TRADE.NBT",
                         "OPENPPC : TRADE.PPC",
                         "OPENUSD : USD",
                         ]
#: Market separator
market_separator      = " : "

#: Our Account
account               = "<your-account-name>"

#: place orders at this spread (in percent)
bridge_spread_percent = 5

#: amount of funds to use in orders (in percent)
bridge_amount_percent = 100
