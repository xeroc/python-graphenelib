import time
import asyncio
import ssl

try:
    from autobahn.asyncio.websocket import WebSocketClientFactory
    from autobahn.websocket.protocol import parseWsUrl
except ImportError:
    raise ImportError("Missing dependency: python-autobahn")
from grapheneapi import GrapheneAPI, GrapheneWebsocketProtocol


class GrapheneWebsocket(GrapheneAPI):

    """ Constructor takes host, port, and login credentials
    """
    def __init__(self, url, username, password,
                 proto=GrapheneWebsocketProtocol):
        ssl, host, port, resource, path, params = parseWsUrl(url)
        GrapheneAPI.__init__(self, host, port, username, password)
        self.url      = url
        self.username = username
        self.password = password
        self.ssl      = ssl
        self.host     = host
        self.port     = port
        self.proto    = proto
        self.proto.username = self.username
        self.proto.password = self.password
        self.factory  = None

    """ Get an object_id by name
    """
    def object_id(self, name, instance=0):
        objects = {
            "NULL"                           :  "1.0.%d",
            "BASE"                           :  "1.1.%d",
            "ACCOUNT"                        :  "1.2.%d",
            "FORCE_SETTLEMENT"               :  "1.3.%d",
            "ASSET"                          :  "1.4.%d",
            "DELEGATE"                       :  "1.5.%d",
            "WITNESS"                        :  "1.6.%d",
            "LIMIT_ORDER"                    :  "1.7.%d",
            "CALL_ORDER"                     :  "1.8.%d",
            "CUSTOM"                         :  "1.9.%d",
            "PROPOSAL"                       :  "1.10.%d",
            "OPERATION_HISTORY"              :  "1.11.%d",
            "WITHDRAW_PERMISSION"            :  "1.12.%d",
            "VESTING_BALANCE"                :  "1.13.%d",
            "WORKER"                         :  "1.14.%d",
            "BALANCE"                        :  "1.15.%d",
            "GLOBAL_PROPERTY"                :  "2.0.%d",
            "DYNAMIC_GLOBAL_PROPERTY"        :  "2.1.%d",
            "INDEX_META"                     :  "2.2.%d",
            "ASSET_DYNAMIC_DATA"             :  "2.3.%d",
            "ASSET_BITASSET_DATA"            :  "2.4.%d",
            "DELEGATE_FEEDS"                 :  "2.5.%d",
            "ACCOUNT_BALANCE"                :  "2.6.%d",
            "ACCOUNT_STATISTICS"             :  "2.7.%d",
            "ACCOUNT_DEBT"                   :  "2.8.%d",
            "TRANSACTION"                    :  "2.9.%d",
            "BLOCK_SUMMARY"                  :  "2.10.%d",
            "ACCOUNT_TRANSACTION_HISTORY"    :  "2.11.%d",
            "WITNESS_SCHEDULE"               :  "2.12.%d",
        }
        return objects[name] % instance

    """ Define Callbacks on Objects for websocket connections
    """
    def setObjectCallbacks(self, callbacks) :
        self.proto.database_callbacks = callbacks

    """ Subscribe to Full Account Updates
    """
    def setAccountsDispatcher(self, accounts, callback) :
        self.proto.accounts = accounts
        self.proto.accounts_callback = callback

    """ Set Event Callbacks
    """
    def setEventCallbacks(self, callbacks) :
        for key in callbacks :
            self.proto.onEventCallbacks[key] = callbacks[key]

    """ Define Callbacks on Market Events for websocket connections
    """
    def setMarketCallBack(self, markets) :
        self.proto.markets = markets

    """ Get_Object as a passthrough from get_objects([array])
        Attention: This call requires GrapheneAPI because it is a non-blocking
        JSON query
    """
    def get_object(self, oid):
        return self.get_objects([oid])[0]

    """ Create websocket factory by Autobahn
    """
    def connect(self) :
        self.factory          = WebSocketClientFactory(self.url, debug=False)
        self.factory.protocol = self.proto

    """ Run websocket forever and wait for events
    """
    def run_forever(self) :
        loop = asyncio.get_event_loop()
        # forward loop into protocol so that we can issue a reset from the
        # protocol:
        self.factory.protocol.setLoop(self.factory.protocol, loop)

        while True :
            try :
                if self.ssl :
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    coro = loop.create_connection(self.factory, self.host,
                                                  self.port, ssl=context)
                else :
                    coro = loop.create_connection(self.factory, self.host,
                                                  self.port, ssl=self.ssl)

                loop.run_until_complete(coro)
                loop.run_forever()
            except KeyboardInterrupt:
                break

            print("Trying to re-connect in 10 seconds!")
            time.sleep(10)

        print("Good bye!")
        loop.close()
