# -*- coding: utf-8 -*-
import ssl
import json
import logging
import websocket
from .rpc import Rpc
from threading import Lock

log = logging.getLogger(__name__)


class Websocket(Rpc):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # We need a lock to ensure thread-safty
        self.__lock = Lock()

    def connect(self):
        log.debug("Trying to connect to node %s" % self.url)
        self._request_id = 0
        if self.url[:3] == "wss":
            ssl_defaults = ssl.get_default_verify_paths()
            sslopt_ca_certs = {"ca_certs": ssl_defaults.cafile}
            self.ws = websocket.WebSocket(sslopt=sslopt_ca_certs)
        else:  # pragma: no cover
            self.ws = websocket.WebSocket()

        self.ws.connect(
            self.url,
            http_proxy_host=self.proxy_host,
            http_proxy_port=self.proxy_port,
            http_proxy_auth=(self.proxy_user, self.proxy_pass)
            if self.proxy_user
            else None,
            proxy_type=self.proxy_type,
        )

        if self.user and self.password:
            self.login(self.user, self.password, api_id=1)

    def disconnect(self):
        if self.ws:
            try:
                self.ws.close()
                self.ws = None
            except Exception:  # pragma: no cover
                pass

    """ RPC Calls
    """

    def rpcexec(self, payload):
        """ Execute a call by sending the payload

            :param json payload: Payload data
            :raises ValueError: if the server does not respond in proper JSON
                format
        """
        if not self.ws:  # pragma: no cover
            self.connect()

        log.debug(json.dumps(payload))

        # Mutex/Lock
        # We need to lock because we need to wait for websocket
        # response but don't want to allow other threads to send
        # requests (that might take less time) to disturb
        self.__lock.acquire()

        # Send over websocket
        try:
            self.ws.send(json.dumps(payload, ensure_ascii=False).encode("utf8"))
            # Receive from websocket
            ret = self.ws.recv()

        finally:
            # Release lock
            self.__lock.release()

        return ret
