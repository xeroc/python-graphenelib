# -*- coding: utf-8 -*-
import aiohttp
import logging
import json

from jsonrpcclient.clients.aiohttp_client import AiohttpClient

from .rpc import Rpc

log = logging.getLogger(__name__)


class Http(Rpc):
    """ RPC Calls
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = aiohttp.ClientSession(loop=kwargs.get("loop"))
        enable_debug = True if log.getEffectiveLevel() == logging.DEBUG else False
        self.client = AiohttpClient(self.session, self.url, basic_logging=enable_debug)

    async def connect(self):
        pass

    async def disconnect(self):
        await self.session.close()

    async def rpcexec(self, *args):
        """ Execute a call by sending the payload

            :param args: args are passed as "params" in json-rpc request:
                {"jsonrpc": "2.0", "method": "call", "params": "[x, y, z]"}
        """
        response = await self.client.request("call", *args)

        # Return raw response (jsonrpcclient does own parsing)
        return response.text
