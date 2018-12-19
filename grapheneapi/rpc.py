# -*- coding: utf-8 -*-
import json
import time
import logging
import requests
import urllib
from .exceptions import RPCError, NumRetriesReached

log = logging.getLogger(__name__)


class Rpc:
    """ This class allows to call API methods synchronously, without
        callbacks.

        :param str url: A single REST endpoint URL
        :param int num_retries: Try x times to num_retries to a node on
               disconnect, -1 for indefinitely
        :param str proxy: Proxy URL (e.g. socks5://localhost:9050),
               None by default.

        Usage:

        .. code-block:: python

            ws = GrapheneHTTPRPC("https://api.node.com")
            print(ws.get_account_count())

    """

    def __init__(self, url, **kwargs):
        self.api_id = {}
        self._request_id = 0

        self.setup_proxy(kwargs)
        self.num_retries = kwargs.get("num_retries", 1)
        self.user = kwargs.get("user")
        self.password = kwargs.get("password")
        self.url = url

    def setup_proxy(self, options):
        proxy_url = options.pop("proxy", None)
        if proxy_url:
            url = urllib.parse.urlparse(proxy_url)
            self.proxy_host = url.hostname
            self.proxy_port = url.port
            self.proxy_type = url.scheme.lower()
            self.proxy_user = url.username
            self.proxy_pass = url.password
            self.proxy_rdns = True
            if not (url.scheme.endswith("h")):
                self.proxy_rdns = False
            else:
                self.proxy_type = self.proxy_type[0 : len(self.proxy_type) - 1]
        else:
            # Defaults (tweakable)
            self.proxy_host = options.pop("proxy_host", None)
            self.proxy_port = options.pop("proxy_port", 80)
            self.proxy_type = options.pop("proxy_type", "http")
            self.proxy_user = options.pop("proxy_user", None)
            self.proxy_pass = options.pop("proxy_pass", None)
            self.proxy_rdns = False
        log.info(
            "Using proxy %s:%d %s" % (self.proxy_host, self.proxy_port, self.proxy_type)
        )

    def get_proxy_url(self):
        if not self.proxy_host:
            return None
        auth = ""
        if self.proxy_user:
            auth = "%s:%s@" % (self.proxy_user, self.proxy_pass)
        url = (
            self.proxy_type
            + "://"
            + auth
            + ("%s:%d" % (self.proxy_host, self.proxy_port))
        )
        return url

    def get_request_id(self):
        self._request_id += 1
        return self._request_id

    def connect(self):
        pass

    def disconnect(self):
        pass

    def parse_response(self, query):
        ret = {}
        try:
            ret = json.loads(query, strict=False)
        except ValueError:  # pragma: no cover  pragma: no branch
            raise ValueError("Client returned invalid format. Expected JSON!")

        log.debug(json.dumps(query))

        if "error" in ret:  # pragma: no cover
            if "detail" in ret["error"]:
                raise RPCError(ret["error"]["detail"])
            else:
                raise RPCError(ret["error"]["message"])
        else:
            return ret["result"]

    def __getattr__(self, name):
        """ Map all methods to RPC calls and pass through the arguments
        """

        def method(*args, **kwargs):

            # Sepcify the api to talk to
            if "api_id" not in kwargs:  # pragma: no cover
                if "api" in kwargs:
                    if kwargs["api"] in self.api_id and self.api_id[kwargs["api"]]:
                        api_id = self.api_id[kwargs["api"]]
                    else:
                        api_id = kwargs["api"]
                else:
                    api_id = 0
            else:  # pragma: no cover
                api_id = kwargs["api_id"]

            # let's be able to define the num_retries per query
            self.num_retries = kwargs.get("num_retries", self.num_retries)

            query = {
                "method": "call",
                "params": [api_id, name, list(args)],
                "jsonrpc": "2.0",
                "id": self.get_request_id(),
            }
            r = self.rpcexec(query)
            message = self.parse_response(r)
            return message

        return method
