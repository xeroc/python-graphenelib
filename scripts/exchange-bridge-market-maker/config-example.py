wallet_host           = "localhost"
wallet_port           = 8092
wallet_user           = ""
wallet_password       = ""
witness_url           = "ws://10.0.0.16:8090/"
witness_user          = ""
witness_password      = ""

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
market_separator      = " : "
account               = "<your-account-name>"

#: place orders at this spread (in percent)
bridge_spread_percent = 5

#: amount of funds to use in orders (in percent)
bridge_amount_percent = 100
