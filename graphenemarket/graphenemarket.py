from grapheneapi import GrapheneAPI, GrapheneWebsocketProtocol
from datetime import datetime
import time


class GrapheneMarket(GrapheneWebsocketProtocol) :
    markets = {}
    account = ""
    wallet = None

    def __init__(self, config) :
        super().__init__()
        self.wallet = GrapheneAPI(config.wallet_host,
                                  config.wallet_port,
                                  config.wallet_user,
                                  config.wallet_password)

    def formatTimeFromNow(self, secs):
        return datetime.utcfromtimestamp(time.time() + int(secs)).strftime('%Y-%m-%dT%H:%M:%S')

    """ Poloniex compatible API
        #######################
    """

"""
    def returnTicker(self):
        r = {}
        for market in self.markets :
            print(self.markets)
            m = self.markets[market]
            marketHistory = client.rpc.get_market_history(
                m["quote"], m["base"], 24 * 60 * 60)
            orders = client.rpc.get_limit_orders(
                m["quote"], m["base"], 1)
            filled = self.rpc.get_fill_order_history(
                m["quote"], m["base"], 1, api_id=2)
            print(orders)
            data = {}
            data["last"]          = 0
            data["lowestAsk"]     = orders[1]["quote"] / orders[1]["base"]
            data["highestBid"]    = orders[0]["quote"] / orders[1]["base"]
            data["percentChange"] = 0
            data["baseVolume"]    = marketHistory[0]["base_volume"]
            data["quoteVolume"]   = marketHistory[0]["quote_volume"]
            r.update({market : data})
        return r

    def return24Volume(self):
        pass

    def returnOrderBook(self, currencyPair):
        pass

    def returnMarketTradeHistory(self, currencyPair):
        pass

    def returnBalances(self):
        # Returns all of your balances.
        # Outputs:
        # {"BTC":"0.59098578","LTC":"3.31117268", ... }
        pass

    # Returns your open orders for a given market, specified by the "currencyPair" POST parameter, e.g. "BTC_XCP"
    # Inputs:
    # currencyPair  The currency pair e.g. "BTC_XCP"
    # Outputs:
    # orderNumber   The order number
    # type          sell or buy
    # rate          Price the order is selling or buying at
    # Amount        Quantity of order
    # total         Total value of order (price * quantity)
    def returnOpenOrders(self, currencyPair):
        return self.api_query('returnOpenOrders',{"currencyPair":currencyPair})

    # Returns your trade history for a given market, specified by the "currencyPair" POST parameter
    # Inputs:
    # currencyPair  The currency pair e.g. "BTC_XCP"
    # Outputs:
    # date          Date in the form: "2014-02-19 03:44:59"
    # rate          Price the order is selling or buying at
    # amount        Quantity of order
    # total         Total value of order (price * quantity)
    # type          sell or buy
    def returnTradeHistory(self, currencyPair):
        return self.api_query('returnTradeHistory', {"currencyPair" : currencyPair})

    # Places a buy order in a given market. Required POST parameters are "currencyPair", "rate", and "amount". If successful, the method will return the order number.
    # Inputs:
    # currencyPair  The curreny pair
    # rate          price the order is buying at
    # amount        Amount of coins to buy
    # Outputs:
    # orderNumber   The order number
    def buy(self, currencyPair, rate, amount):
        return self.api_query('buy', {"currencyPair" : currencyPair, "rate" : rate , "amount" : amount})

    # Places a sell order in a given market. Required POST parameters are "currencyPair", "rate", and "amount". If successful, the method will return the order number.
    # Inputs:
    # currencyPair  The curreny pair
    # rate          price the order is selling at
    # amount        Amount of coins to sell
    # Outputs:
    # orderNumber   The order number
    def sell(self, currencyPair, rate, amount):
        return self.api_query('sell', {"currencyPair" : currencyPair, "rate" : rate, "amount":amount})

    # Cancels an order you have placed in a given market. Required POST parameters are "currencyPair" and "orderNumber".
    # Inputs:
    # currencyPair  The curreny pair
    # orderNumber   The order number to cancel
    # Outputs:
    # succes        1 or 0
    def cancel(self, currencyPair, orderNumber):
        return self.api_query('cancelOrder', {"currencyPair":currencyPair,"orderNumber":orderNumber})

    # Immediately places a withdrawal for a given currency, with no email confirmation. In order to use this method, the withdrawal privilege must be enabled for your API key. Required POST parameters are "currency", "amount", and "address". Sample output: {"response":"Withdrew 2398 NXT."}
    # Inputs:
    # currency      The currency to withdraw
    # amount        The amount of this coin to withdraw
    # address       The withdrawal address
    # Outputs:
    # response      Text containing message about the withdrawal
    def withdraw(self, currency, amount, address):
        return self.api_query('withdraw',{"currency":currency, "amount":amount, "address":address})

    " Other Calls
        #######################
    "

    def get_asset_id(self, asset):
        return self.client.blockchain_get_asset(asset)["result"]["id"]

    def get_precision(self, asset):
        return float(self.client.blockchain_get_asset(asset)["result"]["precision"])

    def get_centerprice(self, quote, base):
        return float(self.client.blockchain_market_status(quote, base)["result"]["center_price"]["ratio"])

    def get_lowest_ask(self, asset1, asset2):
        return float(self.client.blockchain_market_order_book(asset1, asset2)["result"][1][0]["market_index"]["order_price"]["ratio"])

    def get_lowest_bid(self, asset1, asset2):
        return float(self.client.blockchain_market_order_book(asset1, asset2)["result"][0][0]["market_index"]["order_price"]["ratio"])

    def get_balance(self, account, asset):
        pass

    def cancel_all_orders(self, account, quote, base):
        pass

    def ask_at_market_price(self, name, amount, base, quote, confirm=False) :
        pass

    def bid_at_market_price(self, name, amount, base, quote, confirm=False) :
        pass

    def submit_bid(self, account, amount, quote, price, base):
        pass

    def submit_ask(self, account, amount, quote, price, base):
        pass

    def get_bids_less_than(self, account, quote, base, price):
        pass

    def get_all_orders(self, account, quote, base):
        pass

    def get_last_fill(self, quote, base):
        pass

    def get_price(self, quote, base):
        pass
"""
