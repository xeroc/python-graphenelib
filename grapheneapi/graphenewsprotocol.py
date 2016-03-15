import json
from functools import partial

try:
    from autobahn.asyncio.websocket import WebSocketClientProtocol
except ImportError:
    raise ImportError("Missing dependency 'autobahn'.")


class GrapheneWebsocketProtocol(WebSocketClientProtocol):
    """ Graphene Websocket Protocol is the class that will be used
        within the websocket subsystem Autobahn to interact with your
        API on messages, notifications, and events.

        This class handles the actual calls and graphene-specific
        behavior.
    """

    #: loop will be used to indicate the loss of connection
    loop = None

    #: Database callbacks and IDs for object subscriptions
    database_callbacks = {}
    database_callbacks_ids = {}

    #: Accounts and callbacks for account updates
    accounts = []
    accounts_callback = None

    #: Markets to subscribe to
    markets = []

    #: Storage of Objects to reduce latency and load
    objectMap = None

    #: Event Callback registrations and fnts
    onEventCallbacks = {}

    #: Registered APIs with corresponding API-IDs
    api_ids    = {}

    #: Incremental Request ID and request storage (FIXME: request storage
    #: is not cleaned up)
    request_id = 0
    requests   = {}

    def __init__(self):
        pass

    def wsexec(self, params, callback=None):
        """ Internally used method to execute calls

            :param json params: parameters defining the actual call
            :param fnt callback: Callback to be executed upon receiption
                                 of the answer (defaults to ``None``)
        """
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
        """ Call an event callback

            :param str name: Name of the event
        """
        if (name in self.onEventCallbacks and
           callable(self.onEventCallbacks[name])):
            self.onEventCallbacks[name](self)

    def register_api(self, name):
        """ Register to an API of graphene

            :param str name: Name of the API (e.g. database, history,
                             ...)
        """
        self.wsexec([1, name, []], [partial(self._set_api_id, name)])

    def _set_api_id(self, name, data):
        """ Set the API id as returned from the server

            :param str name: Name of the API
            :param int data: API id as returned by the server

        """
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
        """ Login to the API
        """
        self.wsexec([1, "login", [self.username, self.password]])

    def subscribe_to_accounts(self, account_ids, *args):
        """ Subscribe to account ids

            :param account_ids: Account ids to register to
            :type account_ids: Array of account IDs

        """
        self.wsexec([0, "get_full_accounts", [account_ids, True]])

    def subscribe_to_markets(self, dummy=None):
        """ Subscribe to the markets as defined in ``self.markets``.
        """
        for m in self.markets:
            market = self.markets[m]
            self.request_id += 1
            self.wsexec([0, "subscribe_to_market",
                         [self.request_id,
                          market["quote"],
                          market["base"]]])

    def subscribe_to_objects(self, *args):
        """ Subscribe to objects as described in

            * ``self.database_callbacks``
            * ``self.accounts``

            and set the subscription callback.
        """
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

    def getAccountHistory(self, account_id, callback,
                          start="1.11.0", stop="1.11.0", limit=100):
        """ Get Account history History and call callback

            :param account-id account_id: Account ID to read the history for
            :param fnt callback: Callback to execute with the response
            :param historyID start: Start of the history (defaults to ``1.11.0``)
            :param historyID stop: Stop of the history (defaults to ``1.11.0``)
            :param historyID stop: Limit entries by (defaults to ``100``, max ``100``)
            :raises ValueError: if the account id is incorrectly formatted
        """
        if account_id[0:4] == "1.2." :
            self.wsexec([self.api_ids["history"],
                        "get_account_history",
                         [account_id, start, 100, stop]],
                        callback)
        else :
            raise ValueError("getAccountHistory expects an account" +
                             "id of the form '1.2.x'!")

    def getAccountProposals(self, account_ids, callback):
        """ Get Account Proposals and call callback

            :param array account_ids: Array containing account ids
            :param fnt callback: Callback to execute with the response

        """
        self.wsexec([self.api_ids["database"],
                    "get_proposed_transactions",
                     account_ids],
                    callback)

    def dispatchNotice(self, notice):
        """ Main Message Dispatcher for notifications as called by
            ``onMessage``. This dispatcher will separated object,
            account and market updates from each other and call the
            corresponding callbacks.

            :param json notice: Notice from the API

        """
        if "id" not in notice:
            return
        oid = notice["id"]
        [inst, _type, _id] = oid.split(".")
        account_ids = []
        for a in self.accounts :
            account_ids.append("2.6.%s" % a.split(".")[2])  # account history
            account_ids.append("1.2.%s" % a.split(".")[2])  # account
        try:
            " Object Subscriptions "
            if (oid in self.database_callbacks_ids and
               callable(self.database_callbacks_ids[oid])):
                self.database_callbacks_ids[oid](self, notice)

            " Account Notifications "
            if (callable(self.accounts_callback) and
                    (oid in account_ids or  # account updates
                     inst == "1" and _type == "10")):  # proposals
                self.accounts_callback(notice)

            " Market notifications "
            if inst == "1" and _type == "7":
                for m in self.markets:
                    market = self.markets[m]
                    if(((market["quote"] == notice["sell_price"]["quote"]["asset_id"] and
                       market["base"] == notice["sell_price"]["base"]["asset_id"]) or
                       (market["base"] == notice["sell_price"]["quote"]["asset_id"] and
                       market["quote"] == notice["sell_price"]["base"]["asset_id"])) and
                       callable(market["callback"])):
                        market["callback"](self, notice)

        except Exception as e:
            print('Error dispatching notice: %s' % str(e))
            import traceback
            traceback.print_exc()

    def getObjectcb(self, oid, callback, *args):
        """ Get an Object from the internal object storage if available
            or otherwise retrieve it from the API.

            :param object-id oid: Object ID to retrieve
            :param fnt callback: Callback to call if object has been received
        """
        if self.objectMap is not None and oid in self.objectMap and callable(callback):
            callback(self.objectMap[oid])
        else:
            handles = [partial(self.setObject, oid)]
            if callback and callable(callback):
                handles.append(callback)
            self.wsexec([self.api_ids["database"],
                         "get_objects",
                         [[oid]]], handles)

    def setObject(self, oid, data):
        """ Set Object in the internal Object Storage
        """
        if self.objectMap is not None:
            self.objectMap[oid] = data

    def onConnect(self, response):
        """ Is executed on successful connect. Calls event
            ``connection-init``.
        """
        self.request_id = 1
        print("Server connected: {0}".format(response.peer))
        self.eventcallback("connection-init")

    def onOpen(self):
        """ Called if connection Opened successfully. Logs into the API,
            requests access to APIs and calls event
            ``connection-opened``.
        """
        print("WebSocket connection open.")
        self._login()

        " Register with database "
        self.wsexec([1, "database", []], [
            partial(self._set_api_id, "database"),
            self.subscribe_to_objects,
            self.subscribe_to_markets])

        self.register_api("history")
#       self.register_api("network_node")
        self.register_api("network_broadcast")
        self.eventcallback("connection-opened")

    def onMessage(self, payload, isBinary):
        """ Main websocket message dispatcher.

            This message separates distinct client initiated responses
            from server initiated event-driven notifications and either
            calls the corresponding callback or the notification
            dispatcher.

            :param binary payload: data received through the connection
            :param bool isBinary: Flag to indicate binary nature of the
                                  payload
        """
        res = json.loads(payload.decode('utf8'))
#        print("\n\nServer: " + json.dumps(res,indent=1))
#        print("\n\nServer: " + str(res))
        if "error" not in res:
            " Resolve answers from RPC calls "
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
                " Run registered call backs for individual object notices "
                if res["method"] == "notice":
                    [self.setObject(notice["id"], notice)
                        for notice in res["params"][1][0] if "id" in notice]
                    [self.dispatchNotice(notice)
                        for notice in res["params"][1][0] if "id" in notice]
        else:
            print("Error! ", res)

    def setLoop(self, loop):
        """ Define the asyncio loop so that it can be halted on
            disconnects
        """
        self.loop = loop

    def connection_lost(self, errmsg):
        """ Is called if the connection is lost. Calls event
            ``connection-closed`` and closes the asyncio main loop.
        """
        print("WebSocket connection closed: {0}".format(errmsg))
        self.loop.stop()
        self.eventcallback("connection-closed")
