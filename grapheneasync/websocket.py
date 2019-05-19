import asyncio
import websockets
import logging
import json

from .rpc import Rpc

log = logging.getLogger(__name__)


class Websocket(Rpc):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ws = None
        self.loop = kwargs.get('loop')

    async def connect(self):
        self.ws = await websockets.connect(self.url, ssl=True, loop=self.loop)

    async def disconnect(self):
        await self.ws.close()

    async def rpcexec(self, payload):
        if not self.ws:
            await self.connect()

        log.debug(json.dumps(payload))

        await self.ws.send(json.dumps(payload))

        return await self.ws.recv()
