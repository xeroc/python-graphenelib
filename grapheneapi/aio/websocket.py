# -*- coding: utf-8 -*-
import asyncio
import websockets
import logging
import json

from jsonrpcclient.clients.websockets_client import WebSocketsClient
from jsonrpcclient.exceptions import ReceivedErrorResponseError

from .rpc import Rpc

log = logging.getLogger(__name__)


class Websocket(Rpc):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ws = None
        self.client = None

    async def connect(self):
        ssl = True if self.url[:3] == "wss" else None
        self.ws = await websockets.connect(self.url, ssl=ssl, loop=self.loop)
        enable_debug = True if log.getEffectiveLevel() == logging.DEBUG else False
        self.client = WebSocketsClient(self.ws, basic_logging=enable_debug)

    async def disconnect(self):
        if self.ws:
            await self.ws.close()

    async def rpcexec(self, *args):
        """ Execute a RPC call

            :param args: args are passed as "params" in json-rpc request:
                {"jsonrpc": "2.0", "method": "call", "params": "[x, y, z]"}
        """
        if not self.ws:
            await self.connect()

        try:
            response = await self.client.request("call", *args)
        except ReceivedErrorResponseError as e:
            # Extract error data from ErrorResponse object
            response = {
                "error": {
                    "message": e.response.message,
                    "data": e.response.data,
                    "code": e.response.code,
                }
            }
            return json.dumps(response)

        # Return raw response (jsonrpcclient does own parsing)
        return response.text
