# -*- coding: utf-8 -*-
import asyncio
import json
import logging

from grapheneapi.rpc import Rpc as SyncRpc

log = logging.getLogger(__name__)


class Rpc(SyncRpc):
    def __init__(self, url, *args, loop=None, **kwargs):
        self.api_id = {}
        self._request_id = 0
        self.url = url
        self.loop = kwargs.get(loop, asyncio.get_event_loop())

    def __getattr__(self, name):
        """ Map all methods to RPC calls and pass through the arguments

            This method is actually defined in RPC class, but we need to
            overwrite this here so that we can use async/await.
        """

        async def method(*args, **kwargs):

            # Sepcify the api to talk to
            if "api_id" not in kwargs:  # pragma: no cover
                if "api" in kwargs:
                    if kwargs["api"] in self.api_id and self.api_id[kwargs["api"]]:
                        api_id = self.api_id[kwargs["api"]]
                    else:
                        api_id = kwargs["api"]
                else:
                    api_id = 0
            else:  # pragma: no cover
                api_id = kwargs["api_id"]

            # let's be able to define the num_retries per query
            self.num_retries = kwargs.get("num_retries", self.num_retries)

            query = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": [api_id, name, list(args)],
                "id": self.get_request_id(),
            }

            # Need to await here!
            r = await self.rpcexec(query)
            message = self.parse_response(r)

            return message

        return method

    def parse_response(self, *args, **kwargs):
        # Disable logging in parent method because we're logging via client libraries
        return super().parse_response(*args, log_on_debug=False, **kwargs)
