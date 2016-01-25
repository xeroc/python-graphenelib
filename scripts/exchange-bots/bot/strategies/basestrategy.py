from grapheneexchange import GrapheneExchange
import json
import os


class BaseStrategy():

    def __init__(self, *args, **kwargs):
        self.state = {"orders" : {}}

        for arg in args :
            if isinstance(arg, GrapheneExchange):
                self.dex = arg
        for key in kwargs:
            setattr(self, key, kwargs[key])

        if "name" not in kwargs:
            raise ValueError("Missing parameter 'name'!")
        self.filename = "data_%s.json" % self.name
        self.settings = self.config.bots[self.name]
        self.opened_orders = []
        self.restore()

    def cancel_all(self, side="both") :
        onceCanceled = False
        curOrders = self.dex.returnOpenOrders()
        for m in self.settings["markets"]:
            if m in curOrders:
                for o in curOrders[m]:
                    if o["type"] is side or side is "both":
                        try :
                            print("Canceling %s" % o["orderNumber"])
                            self.dex.cancel(o["orderNumber"])
                            onceCanceled = True
                        except:
                            print("An error has occured when trying to cancel order %s!" % o)
        return onceCanceled

    def cancel_mine(self, side="both") :
        curOrders = self.dex.returnOpenOrders()
        state = self.getState()
        onceCanceled = False
        for o in state["orders"]:
            for m in self.settings["markets"]:
                if o in curOrders[m] :
                    if o["type"] is side or side is "both":
                        try :
                            print("Canceling %s" % o["orderNumber"])
                            self.dex.cancel(o["orderNumber"])
                            onceCanceled = True
                        except:
                            print("An error has occured when trying to cancel order %s!" % o["orderNumber"])
        return onceCanceled

    def cancel_this_markets(self) :
        orders = self.dex.returnOpenOrders()
        onceCanceled = False
        for m in self.settings["markets"]:
            for o in orders[m]:
                try :
                    print("Canceling %s" % o["orderNumber"])
                    self.dex.cancel(o["orderNumber"])
                    onceCanceled = True
                except:
                    print("An error has occured when trying to cancel order %s!" % o["orderNumber"])
        return onceCanceled

    def cancel_all_sell_orders(self):
        return self.cancel_all("sell")

    def cancel_all_buy_orders(self):
        return self.cancel_all("buy")

    def cancel_my_sell_orders(self):
        return self.cancel_mine("sell")

    def cancel_my_buy_orders(self):
        return self.cancel_mine("buy")

    def cancel_all_bid_orders(self):
        return self.cancel_all("buy")

    def cancel_all_ask_orders(self):
        return self.cancel_all("sell")

    def cancel_my_bid_orders(self):
        return self.cancel_my_buys()

    def cancel_my_ask_orders(self):
        return self.cancel_my_sells()

    def getState(self):
        return self.state

    def setState(self, state):
        self.state = state

    def store(self):
        state = self.getState()
        myorders = state["orders"]
        curOrders = self.dex.returnOpenOrdersIds()
        for market in self.settings["markets"] :
            if market not in myorders:
                myorders[market] = []
            if market in curOrders:
                for orderid in curOrders[market] :
                    if market not in self.opened_orders or \
                            orderid not in self.opened_orders[market] :
                        myorders[market].append(orderid)
                        self.orderPlaced(orderid)

        state["orders"] = myorders
        with open(self.filename, 'w') as fp:
            json.dump(state, fp)

    def restore(self):
        if os.path.isfile(self.filename) :
            with open(self.filename, 'r') as fp:
                state = json.load(fp)
                self.setState(state)

    def loadMarket(self):
        print("Loading market")
        #: Load Open Orders for the markets and store them for later
        self.opened_orders = self.dex.returnOpenOrdersIds()

        #: Have orders been matched?
        old_orders = self.getState()["orders"]
        cur_orders = self.dex.returnOpenOrdersIds()
        for market in self.settings["markets"] :
            if market in old_orders:
                for orderid in old_orders[market] :
                    if orderid not in cur_orders[market] :
                        self.orderMatched(orderid)
                        # Remove it from the state
                        self.state["orders"][market].remove(orderid)

    def sell(self, market, price, amount):
        quote, base = market.split(self.config.market_separator)
        print(" - Selling %f %s for %s @%f %s/%s" % (amount, quote, base, price, quote, base))
        self.dex.sell(market, price, amount)

    def buy(self, market, price, amount):
        quote, base = market.split(self.config.market_separator)
        print(" - Buying %f %s with %s @%f %s/%s" % (amount, quote, base, price, quote, base))
        self.dex.buy(market, price, amount)

    def place(self) :
        pass

    def init(self) :
        print("Initializing %s" % self.name)

    def tick(self) :
        pass

    def orderMatched(self, oid):
        print("An order has been matched: %s" % oid)

    def orderPlaced(self, oid):
        print("New Order %s" % oid)
