import json
from functools import partial
try:
    from autobahn.asyncio.websocket import WebSocketClientProtocol
except ImportError:
    raise ImportError("Missing dependency: python-autobahn")

"""
Graphene Websocket Protocol
"""


class GrapheneWebsocketProtocol(WebSocketClientProtocol):
    loop = None
    database_callbacks = {}
    database_callbacks_ids = {}  # sorted by subscription ids
    accounts = []
    accounts_callback = None
    markets = []
    objectMap = {}
    onEventCallbacks = {}
    api_ids    = {}
    request_id = 0
    requests   = {}

    def __init__(self):
        pass

    def wsexec(self, params, callback=None):
        request = {"request" : {}, "callback" : None}
        self.request_id += 1
        request["id"] = self.request_id
        request["request"]["id"] = self.request_id
        request["request"]["method"] = "call"
        request["request"]["params"] = params
        request["callback"] = callback
        self.requests.update({self.request_id: request})
#        print(json.dumps(request["request"],indent=4))
#        print(request["request"])
        self.sendMessage(json.dumps(request["request"]).encode('utf8'))

    def eventcallback(self, name):
        if (name in self.onEventCallbacks and
           callable(self.onEventCallbacks[name])):
            self.onEventCallbacks[name](self)

    def _set_api_id(self, name, data):
        self.api_ids.update({name : data})
        if name == "database":
            self.eventcallback("registered-database")
        elif name == "history":
            self.eventcallback("registered-history")
        elif name == "network_broadcast":
            self.eventcallback("registered-network-broadcast")
        elif name == "network_node":
            self.eventcallback("registered-network-node")

    def _login(self):
        self.wsexec([1, "login", [self.username, self.password]])

    def getObjectcb(self, oid, callback, *args):
        if oid in self.objectMap and callable(callback):
            callback(self.objectMap[oid])
        else:
            handles = [partial(self.setObject, oid)]
            if callback and callable(callback):
                handles.append(callback)
            self.wsexec([self.api_ids["database"],
                         "get_objects",
                         [[oid]]], handles)

    def setObject(self, oid, data):
        self.objectMap[oid] = data

    def subscribe_to_accounts(self, account_ids, *args):
        self.wsexec([0, "get_full_accounts", [account_ids, True]])

    def subscribe_to_markets(self, dummy):
        for market in self.markets:
            self.request_id += 1
            self.wsexec([0, "subscribe_to_market",
                         [self.request_id,
                          market["quote"],
                          market["base"]]])

    def subscribe_to_objects(self, *args):
        handles = []
        for handle in self.database_callbacks:
            handles.append(partial(self.getObjectcb, handle, None))
            self.database_callbacks_ids.update({
                handle: self.database_callbacks[handle]})

        if self.accounts:
            handles.append(partial(self.subscribe_to_accounts, self.accounts))
        self.request_id += 1
        self.wsexec([self.api_ids["database"],
                     "set_subscribe_callback",
                     [self.request_id, False]], handles)

    def dispatchNotice(self, notice):
        if "id" not in notice:
            return
        oid = notice["id"]
        [inst, _type, _id] = oid.split(".")
        try:
            if (oid in self.database_callbacks_ids and
               callable(self.database_callbacks_ids[oid])):
                self.database_callbacks_ids[oid](self, notice)

            " Account Notifications "
            if (callable(self.accounts_callback) and
                (("2.6.%s" % _id in self.accounts) or
                 ("1.2.%s" % _id in self.accounts))):
                self.accounts_callback(notice)

            " Market notifications "
            if inst == "1" and _type == "7":
                for market in self.markets:
                    if(((market["quote"] == notice["sell_price"]["quote"]["asset_id"] and
                       market["base"] == notice["sell_price"]["base"]["asset_id"]) or
                       (market["base"] == notice["sell_price"]["quote"]["asset_id"] and
                       market["quote"] == notice["sell_price"]["base"]["asset_id"])) and
                       callable(market["callback"])):
                        market["callback"](self, notice)

        except Exception as e:
            print('Error dispatching notice: %s' % str(e))

    def register_api(self, name):
        self.wsexec([1, name, []], [partial(self._set_api_id, name)])

    ################
    # Websocket API
    ################
    def onConnect(self, response):
        self.request_id = 1
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        print("WebSocket connection open.")
        self._login()

        """ Register with database
        """
        self.wsexec([1, "database", []], [
            partial(self._set_api_id, "database"),
            self.subscribe_to_objects,
            self.subscribe_to_markets])

        self.register_api("history")
#       self.register_api("network_node")
        self.register_api("network_broadcast")

    def onMessage(self, payload, isBinary):
        res = json.loads(payload.decode('utf8'))
#        print("\n\nServer: " + json.dumps(res,indent=1))
#        print("\n\nServer: " + str(res))
        if "error" not in res:
            """ Resolve answers from RPC calls
            """
            if "id" in res:
                if res["id"] not in self.requests:
                    print("Received answer to an unknown request?!")
                else:
                    callbacks = self.requests[res["id"]]["callback"]
                    if callable(callbacks):
                        callbacks(res["result"])
                    elif isinstance(callbacks, list):
                        for callback in callbacks:
                            callback(res["result"])
            elif "method" in res:
                """ Run registered call backs for individual object notices
                """
                if res["method"] == "notice":
                    [self.setObject(notice["id"], notice)
                        for notice in res["params"][1][0] if "id" in notice]
                    [self.dispatchNotice(notice)
                        for notice in res["params"][1][0] if "id" in notice]
        else:
            print("Error! ", res)

    def setLoop(self, loop):
        self.loop = loop

    def connection_lost(self, errmsg):
        print("WebSocket connection closed: {0}".format(errmsg))
        self.loop.stop()
