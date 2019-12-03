# -*- coding: utf-8 -*-
import aiohttp
import logging
import json

from .rpc import Rpc

log = logging.getLogger(__name__)


class Http(Rpc):
    """ RPC Calls
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = aiohttp.ClientSession(loop=kwargs.get("loop"))
        self.notifications = None

    async def connect(self):
        pass

    async def disconnect(self):
        await self.session.close()

    async def rpcexec(self, *args):
        """ Execute a RPC call

            :param args: args are passed as "params" in json-rpc request:
                {"jsonrpc": "2.0", "method": "call", "params": "[x, y, z]", "id": 1}
        """

        request_id = self.get_request_id()
        request = {"jsonrpc": "2.0", "method": "call", "params": args, "id": request_id}

        async with self.session.post(self.url, json=request) as response:
            response_text = await response.text()

        # Return raw response (jsonrpcclient does own parsing)
        return response_text
