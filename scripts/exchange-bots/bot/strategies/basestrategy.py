from grapheneexchange import GrapheneExchange
import json


class BaseStrategy():

    def __init__(self, *args, **kwargs):
        self.state = None

        for arg in args :
            if isinstance(arg, GrapheneExchange):
                self.dex = arg
        for key in kwargs:
            setattr(self, key, kwargs[key])

        if "name" not in kwargs:
            raise ValueError("Missing parameter 'name'!")
        self.filename = "data_%s.json" % self.name

        self.settings = self.config.bots[self.name]
        self.orders = []

    def init(self) :
        print("Initializing %s" % self.name)

    def tick(self) :
        pass

    def cancel_all(self) :
        orders = self.dex.returnOpenOrders()
        for m in orders:
            for order in orders[m]:
                self.dex.cancel(order["orderNumber"])

    def cancel_mine(self) :
        myOrders = []
        for i, d in enumerate(self.orders):
            o = {}
            o["for_sale"] = d["amount_to_sell"]
            myOrders.append(o)

        orders = self.dex.returnOpenOrders()
        for m in orders:
            for order in orders[m]:
                for stored_order in myOrders:
                    print("==========")
                    print(stored_order["for_sale"])
                    print(order["amount_to_sell"])
#                    #self.dex.cancel(order["orderNumber"])

    def save_orders(self, orders):
        for o in orders["operations"] :
            self.orders.append(o[1])

    def place(self) :
        pass

    def getState(self):
        return self.state

    def setState(self, state):
        self.state = state

    def store(self):
        state = self.state()
        with open(self.filename, 'w') as fp:
            json.dump(state, fp)

    def restore(self):
        with open(self.filename, 'r') as fp:
            state = json.load(fp)
            self.setState(state)
