import asyncio
import websockets
import logging
import json

from jsonrpcclient.clients.websockets_client import WebSocketsClient

from .rpc import Rpc

log = logging.getLogger(__name__)


class Websocket(Rpc):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ws = None
        self.client = None

    async def connect(self):
        self.ws = await websockets.connect(self.url, ssl=True, loop=self.loop)
        self.client = WebSocketsClient(self.ws)

    async def disconnect(self):
        await self.ws.close()

    async def rpcexec(self, *args):
        """ Execute a RPC call

            :param args: args are passed as "params" in json-rpc request:
                {"jsonrpc": "2.0", "method": "call", "params": "[x, y, z]"}
        """
        if not self.ws:
            await self.connect()

        log.debug(json.dumps(args))

        response = await self.client.request('call', *args)

        # Return raw response (jsonrpcclient does own parsing)
        return response.text
