from grapheneapi.graphenewsprotocol import GrapheneWebsocketProtocol
from grapheneexchange import GrapheneExchange
import time


class BotProtocol(GrapheneWebsocketProtocol):
    pass


class Bot():

    def __init__(self, config, **kwargs):
        botProtocol = BotProtocol
        [setattr(botProtocol, key, config.__dict__[key]) for key in config.__dict__.keys()]

        self.config = config
        self.dex    = GrapheneExchange(botProtocol, safe_mode=config.safe_mode)

        # Initialize all bots
        self.bots = {}
        for index, name in enumerate(config.bots, 1):
            botClass = config.bots[name]["bot"]
            self.bots[name] = botClass(config=config, name=name,
                                       dex=self.dex, index=index)
            self.bots[name].init()

    def wait_block(self):
        time.sleep(6)

    def cancel_all(self):
        for name in self.bots:
            self.bots[name].loadMarket()
            self.bots[name].cancel_all()
            self.bots[name].store()

    def execute(self):
        for name in self.bots:
            print("Executing bot %s" % name)
            self.bots[name].loadMarket()
            self.bots[name].tick()
            self.bots[name].store()
