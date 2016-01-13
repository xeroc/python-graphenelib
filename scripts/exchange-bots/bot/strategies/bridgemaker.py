from .basestrategy import BaseStrategy

"""
"""


class BridgeMaker(BaseStrategy):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def place(self) :
        print("Placing Orders")
        buy_price  = 1 - self.settings["spread_percentage"] / 200
        sell_price = 1 + self.settings["spread_percentage"] / 200

        #: Amount of Funds available for trading (per asset)
        balances = self.dex.returnBalances()
        asset_ids = []
        amounts = {}
        for market in self.config.watch_markets :
            quote, base = market.split(self.config.market_separator)
            asset_ids.append(base)
            asset_ids.append(quote)
        assets_unique = list(set(asset_ids))
        for a in assets_unique:
            if a in balances :
                amounts[a] = balances[a] * self.settings["volume_percentage"] / 100 / asset_ids.count(a)

        print("Placing Orders:")
        orders = []
        for m in self.config.watch_markets:
            quote, base = m.split(self.config.market_separator)
            if quote in amounts :
                print(" - Selling %f %s for %s @%f" % (amounts[quote], quote, base, sell_price))
                tx = self.dex.sell(m, sell_price, amounts[quote])
                self.add_order(tx)
            elif base in amounts :
                print(" - Buying %f %s with %s @%f" % (amounts[base], base, quote, buy_price))
                tx = self.dex.buy(m, buy_price, amounts[base] * buy_price)
                self.add_order(tx)
            else:
                continue
        self.update_orders()
