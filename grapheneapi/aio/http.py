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

    async def rpcexec(self, payload):
        """ Execute a RPC call

            :param dict payload: json-rpc request in format:
                {"jsonrpc": "2.0", "method": "call", "params": "[x, y, z]", "id": 1}
        """
        async with self.session.post(self.url, json=payload) as response:
            response_text = await response.text()

        return response_text
