from .basestrategy import BaseStrategy, MissingSettingsException
from pprint import pprint


class RefundFeePool(BaseStrategy):
    """
    Configuration:

    ::

        bots["PoolRefill"] = {"bot" : RefundFeePool,
                              # markets to serve
                              "markets" : ["MKR : BTS", "OPEN.BTC : BTS"],
                              # target_price to place Ramps around (floating number or "feed")
                              "target_fill_rate" : 5000.0,  # in BTS
                              # lower threshold for refil
                              "lower_threshold" : 100.0,  # in BTS
                              # Skip blocks in continuous mode (not smaller than 1)
                              "skip_blocks" : 1,
                              }

    """

    block_counter = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def init(self):
        #: Verify that the markets are against the core asset
        sym = self.dex.core_asset["symbol"]
        for m in self.settings["markets"]:
            if sym != m.split(self.dex.market_separator)[1]:
                raise Exception(
                    "Base needs to be core asset %s" % sym
                )

        """ After startup, execute one tick()
        """
        self.tick()

    def refill_fee_pool(self, quote_symbol, amount):
        pprint(self.dex.rpc.fund_asset_fee_pool(
            self.config.account,
            quote_symbol,
            amount,
            False)
        )


    def tick(self):
        self.block_counter += 1
        if (self.block_counter % self.settings["skip_blocks"]) == 0:
            for m in self.settings["markets"]:
                quote_symbol = m.split(self.dex.market_separator)[0]
                print("Checking fee pool of %s" % quote_symbol)
                asset = self.dex.rpc.get_asset(quote_symbol)
                core_asset = self.dex.getObject("1.3.0")
                asset_data = self.dex.getObject(asset["dynamic_asset_data_id"])
                fee_pool = int(asset_data["fee_pool"]) / 10 ** core_asset["precision"]

                amount = '{:.{prec}f}'.format(self.settings["target_fill_rate"] - fee_pool,
                                              prec=core_asset["precision"])
                if fee_pool < self.settings["lower_threshold"]:
                    self.refill_fee_pool(
                        quote_symbol,
                        amount
                    )


    def orderFilled(self, oid):
        pass

    def place(self) :
        pass
