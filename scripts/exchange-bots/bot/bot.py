from grapheneexchange import GrapheneExchange


class Bot():

    def __init__(self, config, **kwargs):

        self.config = config
        self.dex    = GrapheneExchange(config, safe_mode=True)

        # Initialize all bots
        self.bots = {}
        for name in config.bots:
            self.bots[name] = config.bots[name]["bot"](config=self.config,
                                                       name=name,
                                                       dex=self.dex)
            self.bots[name].init()

    def execute(self):
        for name in self.bots:
            self.bots[name].cancel_mine()
