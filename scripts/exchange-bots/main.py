from bot.strategies.bridgemaker import BridgeMaker
from bot import Bot


class Config():
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

    bots = {}
    bots["BridgeMaker"] = {"bot" : BridgeMaker,
                           "markets" : ["BTC : TRADE.BTC",
                                        "BTC : OPENBTC"],
                           "spread_percentage" : 5,
                           "volume_percentage" : 50,
                           }
    account               = "btc-bridge-maker"

if __name__ == '__main__':
    bot = Bot(Config)
    bot.bots["BridgeMaker"].save_orders({'ref_block_num': 4383, 'expiration': '2016-01-13T13:47:57', 'extensions': [], 'signatures': ['1f53fd4e4717218ac0ef47c6fa144b48378a7ad234e89cb97aed514f16acc042d631458748aee5a5ed86467b0580661c614769fd75207831285dab56d4130aa58f'], 'operations': [[1, {'extensions': [], 'seller': '1.2.100237', 'fill_or_kill': False, 'fee': {'amount': 1000000, 'asset_id': '1.3.0'}, 'min_to_receive': {'amount': 58479, 'asset_id': '1.3.103'}, 'expiration': '2016-01-20T13:47:29', 'amount_to_sell': {'amount': 57017, 'asset_id': '1.3.569'}}]], 'ref_block_prefix': 3665477119})
    bot.bots["BridgeMaker"].save_orders({'ref_block_num': 4383, 'expiration': '2016-01-13T13:47:57', 'extensions': [], 'signatures': ['20285813f0fcab111a7d790d0ec2ad44add31dc9510a593248bd84e8b3abe347295cc51f7c8cb1851933b5229c3e8ef5eaadb3eb1101a52f028c70bf7c082595d4'], 'operations': [[1, {'extensions': [], 'seller': '1.2.100237', 'fill_or_kill': False, 'fee': {'amount': 1000000, 'asset_id': '1.3.0'}, 'min_to_receive': {'amount': 61478, 'asset_id': '1.3.350'}, 'expiration': '2016-01-20T13:47:29', 'amount_to_sell': {'amount': 59979, 'asset_id': '1.3.569'}}]], 'ref_block_prefix': 3665477119})
    bot.execute()
