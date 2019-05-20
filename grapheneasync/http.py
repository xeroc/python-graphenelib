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
        self.session = aiohttp.ClientSession(loop=kwargs.get('loop'))
        self.client = AiohttpClient(self.session, self.url)

    async def connect(self):
        pass

    async def disconnect(self):
        await self.session.close()

    async def rpcexec(self, *args):
        """ Execute a call by sending the payload

            :param args: args are passed as "params" in json-rpc request:
                {"jsonrpc": "2.0", "method": "call", "params": "[x, y, z]"}
        """
        log.debug(json.dumps(args))

        response = await self.client.request('call', *args)

        # Return raw response (jsonrpcclient does own parsing)
        return response.text
