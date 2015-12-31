from grapheneapi import GrapheneAPI, GrapheneWebsocket
import logging as log


class GrapheneClient():
    wallet_host = None
    wallet_port = None
    wallet_user = None
    wallet_password = None
    witness_url = None
    witness_user = None
    witness_password = None
    prefix = None

    rpc = None
    ws  = None

    def __init__(self, config):
        available_features = dir(config)

        """ Connect to wallet node
        """
        if ("wallet_host" in available_features and
                "wallet_port" in available_features):
            self.wallet_host = config.wallet_host
            self.wallet_port = config.wallet_port

            if ("wallet_user" in available_features and
                    "wallet_password" in available_features):
                self.wallet_user = config.wallet_user
                self.wallet_password = config.wallet_password

            self.rpc = GrapheneAPI(self.wallet_host,
                                   self.wallet_port,
                                   self.wallet_user,
                                   self.wallet_password)
            " For compatibility reasons: "
            GrapheneAPI.__init__(self,
                                 self.wallet_host,
                                 self.wallet_port,
                                 self.wallet_user,
                                 self.wallet_password)

            core_asset = self.rpc.get_object("1.3.0")[0]

        """ Connect to Witness Node
        """
        if "witness_url" in available_features:
            self.witness_url = config.witness_url

            if ("witness_user" in available_features and
                    "witness_password" in available_features):
                self.witness_user = config.witness_user
                self.witness_password = config.witness_password

            self.ws = GrapheneWebsocket(self.witness_url,
                                        self.witness_user,
                                        self.witness_password,
                                        proto=config)

            """ Register Call available backs
            """
            if "onPropertiesChange" in available_features:
                self.setObjectCallbacks({"2.0.0": config.onPropertiesChange})
            if "onBlock" in available_features:
                self.setObjectCallbacks({"2.1.0": config.onBlock})
            if ("watch_accounts" in available_features and
                    "onAccountUpdate" in available_features):
                account_ids = []
                for a in config.watch_accounts:
                    account = self.rpc.get_account(a)
                    if "id" in account:
                        account_ids.append(account["id"])
                    else:
                        log.warn("Account %s could not be found" % a)
                self.setAccountsDispatcher(account_ids, config.onAccountUpdate)
            if ("watch_markets" in available_features and
                    "onMarketUpdate" in available_features):
                markets = []
                for market in config.watch_markets:
                    [quote_symbol, base_symbol] = market.split(":")
                    try:
                        quote = self.rpc.get_asset(quote_symbol)
                        base  = self.rpc.get_asset(base_symbol)
                    except:
                        raise Exception("Couldn't load assets for market %s"
                                        % market)
                    if "id" in quote and "id" in base:
                        markets.append({"name"    : market,
                                        "quote"   : quote["id"],
                                        "base"    : base["id"],
                                        "callback": config.onMarketUpdate})
                    else:
                        log.warn("Market assets could not be found: %s"
                                 % market)
                self.setMarketCallBack(markets)
            if "onRegisterHistory" in available_features:
                self.setEventCallbacks(
                    {"registered-history": config.onRegisterHistory})
            if "onRegisterDatabase" in available_features:
                self.setEventCallbacks(
                    {"registered-database": config.onRegisterDatabase})
            if "onRegisterNetworkNode" in available_features:
                self.setEventCallbacks(
                    {"registered-network-node": config.onRegisterNetworkNode})
            if "onRegisterNetworkBroadcast" in available_features:
                self.setEventCallbacks(
                    {"registered-network-broadcast":
                     config.onRegisterNetworkBroadcast})

            core_asset = self.ws.get_object("1.3.0")

        if not core_asset :
            raise Exception("Neither WS nor RPC propery configured!")

        if core_asset["symbol"] == "BTS" :
            self.prefix = "BTS"
        elif core_asset["symbol"] == "MUSE" :
            self.prefix = "MUSE"
        elif core_asset["symbol"] == "CORE" :
            self.prefix = "GPH"

    """ Forward these calls to Websocket API
    """
    def setEventCallbacks(self, callbacks):
        self.ws.setEventCallbacks(callbacks)

    def setAccountsDispatcher(self, accounts, callback):
        self.ws.setAccountsDispatcher(accounts, callback)

    def setObjectCallbacks(self, callbacks):
        self.ws.setObjectCallbacks(callbacks)

    def setMarketCallBack(self, markets):
        self.ws.setMarketCallBack(markets)

    def connect(self):
        self.ws.connect()

    def run_forever(self):
        self.ws.run_forever()

    def run(self):
        self.connect()
        self.run_forever()

    """ Object Store
    """
    def getObject(self, oid):
        print(self.ws)
        if self.ws :
            [_instance, _type, _id] = oid.split(".")
            if (not (oid in self.ws.proto.objectMap) or
                    _instance == "1" and _type == "7"):  # force refresh orders
                data = self.rpc.get_object(oid)
                self.ws.proto.objectMap[oid] = data
            else:
                data = self.ws.proto.objectMap[oid]
            if len(data) == 1 :
                return data[0]
            else:
                return data
        else :
            return self.rpc.get_object(oid)[0]
