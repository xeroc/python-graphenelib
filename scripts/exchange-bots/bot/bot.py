from grapheneapi.graphenewsprotocol import GrapheneWebsocketProtocol
from grapheneexchange import GrapheneExchange
import time


class BotProtocol(GrapheneWebsocketProtocol):
    """ Bot Protocol to interface with websocket notifications
    """

    def onAccountUpdate(self, data):
        pass

    def onMarketUpdate(self, data):
        pass

    def onBlock(self, data) :
        pass

    def onRegisterDatabase(self):
        pass

class Bot():
    """ Main Bot Architecture that deals with non market related,
        general Bot settings and behavior
    """

    def __init__(self, config, **kwargs):
        """
        """
        self.botProtocol = BotProtocol

        # Take the configuration variables and put them in the current
        # instance of BotProtocol. This step is required to let
        # GrapheneExchange know most of our variables as well!
        # We will also be able to hook into websocket messages from
        # within the configuration file!
        [setattr(self.botProtocol, key, config.__dict__[key]) for key in config.__dict__.keys()]

        # Additionally store the whole configuration
        self.config = config

        # Connect to the DEX
        self.dex    = GrapheneExchange(self.botProtocol, safe_mode=config.safe_mode)

        # Initialize all bots
        self.bots = {}
        for index, name in enumerate(config.bots, 1):
            botClass = config.bots[name]["bot"]
            self.bots[name] = botClass(config=config, name=name,
                                       dex=self.dex, index=index)
            # Maybe the strategy/bot has some additional customized
            # initialized besides the basestrategy's __init__()
            self.bots[name].init()

    def wait_block(self):
        """ This is sooo dirty! FIXIT!
        """
        time.sleep(6)

    def cancel_all(self):
        """ Cancel all orders of all markets that are served by the bots
        """
        for name in self.bots:
            self.bots[name].loadMarket()
            self.bots[name].cancel_this_markets()
            self.bots[name].store()

    def execute(self):
        """ Execute the core unit of the bot
        """
        for name in self.bots:
            print("Executing bot %s" % name)
            self.bots[name].loadMarket()
            self.bots[name].tick()
            self.bots[name].store()

    def run(self):
        """ This call will run the bot in **continous mode** and make it
            receive notification from the network
        """
        # self.dex.run()
        raise NotImplementedError
