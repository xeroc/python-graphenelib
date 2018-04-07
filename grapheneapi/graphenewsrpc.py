import websocket
import urllib
import ssl
import json
import time
import logging
from .exceptions import (
    RPCError,
    NumRetriesReached
)
from itertools import cycle
log = logging.getLogger(__name__)


class GrapheneWebsocketRPC(object):
    """ This class allows to call API methods synchronously, without
        callbacks. It logs in and registers to the APIs:

        * database
        * history

        :param str urls: Either a single Websocket URL, or a list of URLs
        :param str user: Username for Authentication
        :param str password: Password for Authentication
        :param Array apis: List of APIs to register to
        :param int num_retries: Try x times to num_retries to a node on
               disconnect, -1 for indefinitely
        :param str proxy: Proxy url (e.g. socks5://localhost:9050),
               None by default. NOTE: relies on underlying websocket
               implementation to support the various proxy types,
               at the moment only 'http' type is supported reliably.

        Available APIs

              * database
              * network_node
              * network_broadcast
              * history

        Usage:

        .. code-block:: python

            ws = GrapheneWebsocketRPC("ws://10.0.0.16:8090","","")
            print(ws.get_account_count())

        .. note:: This class allows to call methods available via
                  websocket. If you want to use the notification
                  subsystem, please use ``GrapheneWebsocket`` instead.

    """
    def __init__(self, urls, user=None, password=None, **kwargs):
        self.api_id = {}
        self._request_id = 0
        if isinstance(urls, list):
            self.urls = cycle(urls)
        else:
            self.urls = cycle([urls])
        self.prepare_proxy(kwargs)
        self.user = user
        self.password = password
        self.num_retries = kwargs.get("num_retries", -1)

        self.wsconnect()
        self.register_apis()

    def get_request_id(self):
        self._request_id += 1
        return self._request_id

    def next(self):
        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass
        self.wsconnect()
        self.register_apis()

    def prepare_proxy(self, options):
        proxy_url = options.pop("proxy", None)
        if proxy_url:
            url = urllib.parse.urlparse(proxy_url)
            self.proxy_host = url.hostname
            self.proxy_port = url.port
            self.proxy_type = url.scheme.lower()
            self.proxy_user = url.username
            self.proxy_pass = url.password
            self.proxy_rdns = True
            if not(url.scheme.endswith('h')):
                self.proxy_rdns = False
            else:
                self.proxy_type = self.proxy_type[0:len(self.proxy_type)-1]
        else:
            # Defaults (tweakable)
            self.proxy_host = options.pop("proxy_host", None)
            self.proxy_port = options.pop("proxy_port", 80)
            self.proxy_type = options.pop("proxy_type", 'http')
            self.proxy_user = options.pop("proxy_user", None)
            self.proxy_pass = options.pop("proxy_pass", None)
            self.proxy_rdns = False

        log.info("Using proxy %s:%d %s" % (self.proxy_host, self.proxy_port, self.proxy_type))

    def wsconnect(self):
        cnt = 0
        while True:
            cnt += 1
            self.url = next(self.urls)
            log.debug("Trying to connect to node %s" % self.url)
            if self.url[:3] == "wss":
                ssl_defaults = ssl.get_default_verify_paths()
                sslopt_ca_certs = {'ca_certs': ssl_defaults.cafile}
                self.ws = websocket.WebSocket(sslopt=sslopt_ca_certs)
            else:
                self.ws = websocket.WebSocket()
            try:
                self.ws.connect(self.url,
                    http_proxy_host = self.proxy_host,
                    http_proxy_port = self.proxy_port,
                    http_proxy_auth = (self.proxy_user,self.proxy_pass) if self.proxy_user else None,
                    proxy_type = self.proxy_type
                )
                break
            except KeyboardInterrupt:
                raise
            except Exception as e:
                log.warning(str(e))
                if (self.num_retries > -1 and
                        cnt > self.num_retries):
                    raise NumRetriesReached()
                sleeptime = (cnt - 1) * 2 if cnt < 10 else 10
                if sleeptime:
                    log.warning(
                        "Lost connection to node during rpcexec(): %s (%d/%d) "
                        % (self.url, cnt, self.num_retries) +
                        "Retrying in %d seconds" % sleeptime
                    )
                    time.sleep(sleeptime)
        if self.user and self.password:
            self.login(self.user, self.password, api_id=1)

    def register_apis(self):
        """
        # We no longer register to those apis separately because we can instead
        # name them when doing a call
        self.api_id["database"] = self.database(api_id=1)
        self.api_id["history"] = self.history(api_id=1)
        self.api_id["network_broadcast"] = self.network_broadcast(api_id=1)
        """
        pass

    """ RPC Calls
    """
    def rpcexec(self, payload):
        """ Execute a call by sending the payload

            :param json payload: Payload data
            :raises ValueError: if the server does not respond in proper JSON
            format
            :raises RPCError: if the server returns an error
        """
        log.debug(json.dumps(payload))
        cnt = 0
        while True:
            cnt += 1

            try:
                self.ws.send(
                    json.dumps(payload, ensure_ascii=False).encode('utf8')
                )
                reply = self.ws.recv()
                break
            except KeyboardInterrupt:
                raise
            except Exception:
                if (self.num_retries > -1 and
                        cnt > self.num_retries):
                    raise NumRetriesReached()
                sleeptime = (cnt - 1) * 2 if cnt < 10 else 10
                if sleeptime:
                    log.warning(
                        "Lost connection to node during rpcexec(): %s (%d/%d) "
                        % (self.url, cnt, self.num_retries) +
                        "Retrying in %d seconds" % sleeptime
                    )
                    time.sleep(sleeptime)

                # retry
                try:
                    self.ws.close()
                    time.sleep(sleeptime)
                    self.wsconnect()
                    self.register_apis()
                except Exception:
                    pass

        ret = {}
        try:
            ret = json.loads(reply, strict=False)
        except ValueError:
            raise ValueError("Client returned invalid format. Expected JSON!")

        log.debug(json.dumps(reply))

        if 'error' in ret:
            if 'detail' in ret['error']:
                raise RPCError(ret['error']['detail'])
            else:
                raise RPCError(ret['error']['message'])
        else:
            return ret["result"]

    # End of Deprecated methods
    ####################################################################
    def __getattr__(self, name):
        """ Map all methods to RPC calls and pass through the arguments
        """
        def method(*args, **kwargs):

            # Sepcify the api to talk to
            if "api_id" not in kwargs:
                if ("api" in kwargs):
                    if (kwargs["api"] in self.api_id and
                            self.api_id[kwargs["api"]]):
                        api_id = self.api_id[kwargs["api"]]
                    else:
                        # Try the query by providing the argument
                        # right away
                        api_id = kwargs["api"]
                        """
                        raise ValueError(
                            "Unknown API! "
                            "Verify that you have registered to %s"
                            % kwargs["api"]
                        )
                        """
                else:
                    api_id = 0
            else:
                api_id = kwargs["api_id"]

            # let's be able to define the num_retries per query
            self.num_retries = kwargs.get("num_retries", self.num_retries)

            query = {"method": "call",
                     "params": [api_id, name, list(args)],
                     "jsonrpc": "2.0",
                     "id": self.get_request_id()}
            r = self.rpcexec(query)
            return r
        return method
