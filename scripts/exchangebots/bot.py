from grapheneapi.graphenewsprotocol import GrapheneWebsocketProtocol
from grapheneexchange import GrapheneExchange
import time

config = None
bots = {}
dex = None


class BotProtocol(GrapheneWebsocketProtocol):
    """ Bot Protocol to interface with websocket notifications and
        forward notices to the bots
    """

    def onAccountUpdate(self, data):
        """ If the account updates, reload every market
        """
        print("Account Update! Notifying bots:")
        for name in bots:
            print(" - %s" % name)
            bots[name].loadMarket()
            bots[name].store()

    def onMarketUpdate(self, data):
        """ If a Market updates upgrades, reload every market
        """
        print("Market Update! Notifying bots:")
        for name in bots:
            print(" - %s" % name)
            bots[name].loadMarket()
            bots[name].store()

    def onBlock(self, data) :
        """ Every block let the bots know via ``tick()``
        """
        for name in bots:
            bots[name].loadMarket()
            bots[name].tick()
            bots[name].store()

    def onRegisterDatabase(self):
        print("Websocket successfully iInitialized!")


def init(conf, **kwargs):
    """ Initialize the Bot Infrastructure and setup connection to the
        network
    """
    global dex, bots, config

    botProtocol = BotProtocol

    # Take the configuration variables and put them in the current
    # instance of BotProtocol. This step is required to let
    # GrapheneExchange know most of our variables as well!
    # We will also be able to hook into websocket messages from
    # within the configuration file!
    [setattr(botProtocol, key, conf.__dict__[key]) for key in conf.__dict__.keys()]

    # Additionally store the whole configuration
    config = conf

    # Connect to the DEX
    dex    = GrapheneExchange(botProtocol, safe_mode=config.safe_mode)

    if dex.rpc.is_locked():
        raise Exception("Your wallet is LOCKED! Please unlock it manually!")

    # Initialize all bots
    for index, name in enumerate(config.bots, 1):
        botClass = config.bots[name]["bot"]
        bots[name] = botClass(config=config, name=name,
                              dex=dex, index=index)
        # Maybe the strategy/bot has some additional customized
        # initialized besides the basestrategy's __init__()
        bots[name].loadMarket()
        bots[name].init()
        bots[name].store()


def wait_block():
    """ This is sooo dirty! FIXIT!
    """
    time.sleep(6)


def cancel_all():
    """ Cancel all orders of all markets that are served by the bots
    """
    for name in bots:
        bots[name].loadMarket(False)
        bots[name].cancel_this_markets()
        bots[name].store()


def execute():
    """ Execute the core unit of the bot
    """
    for name in bots:
        print("Executing bot %s" % name)
        bots[name].loadMarket()
        bots[name].init()
        bots[name].store()


def run():
    """ This call will run the bot in **continous mode** and make it
        receive notification from the network
    """
    dex.run()
