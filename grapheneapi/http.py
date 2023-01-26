# -*- coding: utf-8 -*-
import json
import time
import logging
import requests
from .exceptions import RPCError, HttpInvalidStatusCode
from .rpc import Rpc

log = logging.getLogger(__name__)


class Http(Rpc):
    """RPC Calls"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__request_session = None

    def proxies(self):  # pragma: no cover
        proxy_url = self.get_proxy_url()
        if proxy_url is None:
            return {}
        return {"http": proxy_url, "https": proxy_url}

    def get_request_session(self) -> requests.Session:
        """Store current HTTP session"""
        if self.__request_session is None:
            self.__request_session = requests.Session()
            self.__request_session.proxies.update(self.proxies())

        return self.__request_session

    def rpcexec(self, payload, retry=None):
        """Execute a call by sending the payload

        :param json payload: Payload data
        :raises ValueError: if the server does not respond in proper JSON
                            format
        :raises HttpInvalidStatusCode: if the server returns a status code
            that is not 200
        """
        try:
            query = self.get_request_session().post(self.url, json=payload)
        except requests.exceptions.ConnectionError as e:
            if not retry:
                raise e
            self.__request_session = None
            return self.rpcexec(payload, retry=False)
        if query.status_code != 200:  # pragma: no cover
            raise HttpInvalidStatusCode(
                "Status code returned: {}".format(query.status_code)
            )

        return query.text
