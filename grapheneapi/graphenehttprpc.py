import json
import time
import logging
import requests
from itertools import cycle
from .exceptions import (
    RPCError,
    NumRetriesReached
)
log = logging.getLogger(__name__)


class GrapheneHTTPRPC(object):
    """ This class allows to call API methods synchronously, without
        callbacks.

        :param str urls: Either a single REST endpoint URL, or a list of URLs
        :param int num_retries: Try x times to num_retries to a node on
               disconnect, -1 for indefinitely

        Usage:

        .. code-block:: python

            ws = GrapheneHTTPRPC("https://api.node.com")
            print(ws.get_account_count())

    """
    def __init__(self, urls, **kwargs):
        self.api_id = {}
        self._request_id = 0
        if isinstance(urls, list):
            self.urls = cycle(urls)
        else:
            self.urls = cycle([urls])
        self.num_retries = kwargs.get("num_retries", -1)

    def get_request_id(self):
        self._request_id += 1
        return self._request_id

    def next(self):
        self.url = next(self.urls)

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
            self.url = next(self.urls)

            try:
                query = requests.post(
                    self.url,
                    json=payload
                )
                if query.status_code != 200:
                    raise
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

        ret = {}
        try:
            ret = query.json()
        except ValueError:
            raise ValueError("Client returned invalid format. Expected JSON!")

        log.debug(json.dumps(query.text))

        if 'error' in ret:
            if 'detail' in ret['error']:
                raise RPCError(ret['error']['detail'])
            else:
                raise RPCError(ret['error']['message'])
        else:
            return ret["result"]

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
                        api_id = kwargs["api"]
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
