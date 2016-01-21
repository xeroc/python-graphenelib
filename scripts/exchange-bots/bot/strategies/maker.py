from .basestrategy import BaseStrategy
import math
from numpy import linspace

"""
"""


class MakerSellBuyWalls(BaseStrategy):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tick(self) :
        #self.cancel_mine()
        self.place()

    def place(self) :
        print("Placing Orders:")
        target_price = self.settings["target_price"]

        #: Amount of Funds available for trading (per asset)
        balances = self.dex.returnBalances()
        asset_ids = []
        amounts = {}
        for market in self.settings["markets"] :
            quote, base = market.split(self.config.market_separator)
            asset_ids.append(base)
            asset_ids.append(quote)
        assets_unique = list(set(asset_ids))
        for a in assets_unique:
            if a in balances :
                amounts[a] = balances[a] * self.settings["volume_percentage"] / 100 / asset_ids.count(a)

        ticker = self.dex.returnTicker()
        for m in self.settings["markets"]:

            if isinstance(target_price, float):
                buy_price  = target_price * (1.0 - self.settings["spread_percentage"] / 200)
                sell_price = target_price * (1.0 + self.settings["spread_percentage"] / 200)
            elif (isinstance(target_price, str) and 
                  target_price is "settlement_price" or
                  target_price is "feed" or
                  target_price is "price_feed"):
                if "settlement_price" in ticker[m] :
                    price = ticker[m]["settlement_price"]
                    buy_price  = price * (1.0 - self.settings["spread_percentage"] / 200)
                    sell_price = price * (1.0 + self.settings["spread_percentage"] / 200)
                else :
                    raise Exception("Pair %s does not have a settlement price!" % m)

            quote, base = m.split(self.config.market_separator)
            if quote in amounts :
                if"symmetric_sides" in self.settings and self.settings["symmetric_sides"]:
                    self.sell(m, sell_price, min([amounts[quote], amounts[base] * buy_price]))
                else :
                    self.sell(m, sell_price, amounts[quote])
            if base in amounts :
                if"symmetric_sides" in self.settings and self.settings["symmetric_sides"]:
                    self.buy(m, buy_price, min([amounts[quote], amounts[base] * buy_price]))
                else :
                    self.buy(m, buy_price, amounts[base] * buy_price)

class MakerRamp(BaseStrategy):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tick(self) :
        self.cancel_mine()
        self.place()

    def place(self) :
        print("Placing Orders:")
        #: Amount of Funds available for trading (per asset)
        if "ramp_mode" not in self.settings:
            mode = "linear"
        else :
            mode = self.settings["ramp_mode"]
        target_price = self.settings["target_price"]

        balances = self.dex.returnBalances()
        asset_ids = []
        amounts = {}
        for market in self.settings["markets"]:
            quote, base = market.split(self.config.market_separator)
            asset_ids.append(base)
            asset_ids.append(quote)
        assets_unique = list(set(asset_ids))
        for a in assets_unique:
            if a in balances :
                amounts[a] = balances[a] * self.settings["volume_percentage"] / 100 / asset_ids.count(a)

        ticker = self.dex.returnTicker()
        for m in self.settings["markets"]:

            quote, base = m.split(self.config.market_separator)
            if isinstance(target_price, float):
                price_target = 1.0
            elif (isinstance(target_price, str) and 
                  target_price is "settlement_price" or
                  target_price is "feed" or
                  target_price is "price_feed"):
                if "settlement_price" in ticker[m] :
                    price_target = ticker[m]["settlement_price"]
                else :
                    raise Exception("Pair %s does not have a settlement price!" % m)

            if quote in amounts :
                price_start  = price_target * (1 + self.settings["spread_percentage"] / 200.0)
                price_end    = price_target * (1 + self.settings["ramp_price_percentage"] / 100.0)
                amount           = min([amounts[quote], amounts[base] * (price_start) / 2.0])
                number_orders    = math.floor((self.settings["ramp_price_percentage"] / 100.0 - self.settings["spread_percentage"] / 200.0) / (self.settings["ramp_step_percentage"] / 100.0))
                if mode == "linear" :
                    for price in linspace(price_start, price_end, number_orders) :
                        self.sell(m, price, amount / number_orders)
                elif mode == "exponential" :
                    k = linspace(1 / number_orders, 1, number_orders)
                    k = [v / sum(k) for v in k]
                    order_amounts = [v * amount for v in k]
                    for i, price in enumerate(linspace(price_start, price_end, number_orders)):
                        self.sell(m, price, order_amounts[i])
                else :
                    raise Exception("ramp_mode '%s' not known" % mode)

            if base in amounts :
                price_start  = price_target * (1 - self.settings["spread_percentage"] / 200.0)
                price_end    = price_target * (1 - self.settings["ramp_price_percentage"] / 100.0)
                amount           = min([amounts[quote], amounts[base] * (price_start) / 2.0])
                number_orders    = math.floor((self.settings["ramp_price_percentage"] / 100.0 - self.settings["spread_percentage"] / 200.0) / (self.settings["ramp_step_percentage"] / 100.0))
                if mode == "linear" :
                    for price in linspace(price_start, price_end, number_orders) :
                        self.buy(m, price, amount / number_orders)
                elif mode == "exponential" :
                    k = linspace(1 / number_orders, 1, number_orders)
                    k = [v / sum(k) for v in k]
                    order_amounts = [v * amount for v in k]
                    for i, price in enumerate(linspace(price_start, price_end, number_orders)):
                        self.buy(m, price, order_amounts[i])
                else :
                    raise Exception("ramp_mode '%s' not known" % mode)
