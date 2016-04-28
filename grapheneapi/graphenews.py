import time
import asyncio
import ssl
from collections import OrderedDict

try:
    from autobahn.asyncio.websocket import WebSocketClientFactory
except ImportError:
    raise ImportError("Missing dependency: python-autobahn")

try:
    from autobahn.websocket.protocol import parseWsUrl
except:
    from autobahn.websocket.util import parse_url as parseWsUrl

from .graphenewsprotocol import GrapheneWebsocketProtocol
from .graphenewsrpc import GrapheneWebsocketRPC

#: max number of objects to chache
max_cache_objects = 50


class LimitedSizeDict(OrderedDict):
    """ This class limits the size of the objectMap
    """

    def __init__(self, *args, **kwds):
        self.size_limit = kwds.pop("size_limit", max_cache_objects)
        OrderedDict.__init__(self, *args, **kwds)
        self._check_size_limit()

    def __setitem__(self, key, value):
        OrderedDict.__setitem__(self, key, value)
        self._check_size_limit()

    def _check_size_limit(self):
        if self.size_limit is not None:
            while len(self) > self.size_limit:
                self.popitem(last=False)


class GrapheneWebsocket(GrapheneWebsocketRPC):
    """ This class serves as a management layer for the websocket
        connection and configuration of the websocket sub-protocol.

        In order to receive notifications of object changes from the
        witness, we need to interface with the websockets protocol.

        To do so, we have developed a `GrapheneWebsocketProtocol`, an
        extension to `WebSocketClientProtocol` as provided by
        `autobahn.asyncio.websocket`.
    """

    def __init__(self, url, username, password,
                 proto=GrapheneWebsocketProtocol):
        ssl, host, port, resource, path, params = parseWsUrl(url)
        GrapheneWebsocketRPC.__init__(self, url, username, password)
        self.url      = url
        self.username = username
        self.password = password
        self.ssl      = ssl
        self.host     = host
        self.port     = port
        self.proto    = proto
        self.proto.username = username
        self.proto.password = password
        self.objectMap = LimitedSizeDict()
        self.proto.objectMap = self.objectMap  # this is a reference
        self.factory  = None

    def setObjectCallbacks(self, callbacks) :
        """ Define Callbacks on Objects for websocket connections

            :param json callbacks: A object/callback json structur to
                                   register object updates with a
                                   callback

            The object/callback structure looks as follows:

            .. code-block: json

                {
                    "2.0.0"    : print,
                    "object-id": fnt-callback
                }
        """
        self.proto.database_callbacks = callbacks

    def setAccountsDispatcher(self, accounts, callback) :
        """ Subscribe to Full Account Updates

            :param accounts: Accounts to subscribe to
            :type accounts: array of account IDs
            :param fnt callback: function to be called on notifications
        """
        self.proto.accounts = accounts
        self.proto.accounts_callback = callback

    def setEventCallbacks(self, callbacks) :
        """ Set Event Callbacks of the subsystem

            :param json callbacks: event/fnt json object

            Available events:

            * ``connection-init``
            * ``connection-opened``
            * ``connection-closed``
            * ``registered-database``
            * ``registered-history``
            * ``registered-network-broadcast``
            * ``registered-network-node``

        """
        for key in callbacks :
            self.proto.onEventCallbacks[key] = callbacks[key]

    def setMarketCallBack(self, markets) :
        """ Define Callbacks on Market Events for websocket connections

            :param markets: Array of market pairs to register to
            :type markets: array of asset pairs

            Example

            .. code-block:: python

                setMarketCallBack(["USD:EUR", "GOLD:USD"])

        """
        self.proto.markets = markets

    def get_object(self, oid):
        """ Get_Object as a passthrough from get_objects([array])
            Attention: This call requires GrapheneAPI because it is a non-blocking
            JSON query

            :param str oid: Object ID to fetch
        """
        return self.get_objects([oid])[0]

    def getObject(self, oid):
        if self.objectMap is not None and oid in self.objectMap:
            return self.objectMap[oid]
        else:
            data = self.get_object(oid)
            self.objectMap[oid] = data
            return data

    def connect(self) :
        """ Create websocket factory by Autobahn
        """
        self.factory          = WebSocketClientFactory(self.url)
        self.factory.protocol = self.proto

    def run_forever(self) :
        """ Run websocket forever and wait for events.

            This method will try to keep the connection alive and try an
            autoreconnect if the connection closes.
        """
        if not issubclass(self.factory.protocol, GrapheneWebsocketProtocol) :
            raise Exception("When using run(), we need websocket " +
                            "notifications which requires the " +
                            "configuration/protocol to inherit " +
                            "'GrapheneWebsocketProtocol'")

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
