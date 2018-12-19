# -*- coding: utf-8 -*-
import json
import time
import logging
import requests
from .exceptions import RPCError, HttpInvalidStatusCode
from .rpc import Rpc

log = logging.getLogger(__name__)


class Http(Rpc):
    """ RPC Calls
    """

    def proxies(self):
        proxy_url = self.get_proxy_url()
        if proxy_url is None:
            return None
        return {"http": proxy_url, "https": proxy_url}

    def rpcexec(self, payload):
        """ Execute a call by sending the payload

            :param json payload: Payload data
            :raises ValueError: if the server does not respond in proper JSON
                                format
            :raises HttpInvalidStatusCode: if the server returns a status code
                that is not 200
        """
        log.debug(json.dumps(payload))
        query = requests.post(self.url, json=payload, proxies=self.proxies())
        if query.status_code != 200:  # pragma: no cover
            raise HttpInvalidStatusCode(
                "Status code returned: {}".format(query.status_code)
            )

        return query.text
