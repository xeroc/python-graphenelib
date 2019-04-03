# -*- coding: utf-8 -*-
import json
import asyncio
import websockets


class Rpc:
    def __init__(self, url, *args, **kwargs):
        self.url = url
        self._request_id = 0

    def get_request_id(self):
        self._request_id += 1
        return self._request_id

    async def connect(self):
        self.websocket = await websockets.connect(self.url)

    async def disconnect(self):
        pass

    async def rpcexec(self, payload):
        await self.websocket.send(json.dumps(payload))
        return await self.websocket.recv()

    def __getattr__(self, name):
        """ Map all methods to RPC calls and pass through the arguments

            This method is actually defined in RPC class, but we need to
            overwrite this here so that we can use async/await.
        """

        async def method(*args, **kwargs):
            api_id = kwargs.get("api_id", kwargs.get("api", 0))
            query = {
                "method": "call",
                "params": [api_id, name, list(args)],
                "jsonrpc": "2.0",
                "id": self.get_request_id(),
            }
            # Need to await here!
            return await self.rpcexec(query)

        return method
