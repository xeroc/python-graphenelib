# -*- coding: utf-8 -*-
import asyncio
import logging
from grapheneapi.exceptions import NumRetriesReached

from grapheneapi.api import Api as SyncApi
from .websocket import Websocket
from .http import Http

log = logging.getLogger(__name__)


class Api(SyncApi):
    def __init__(self, *args, **kwargs):
        # We're need to keep class init synchronous, so we're skipping connect()
        super().__init__(connect=False, *args, **kwargs)
        self._chain_props = None

    def updated_connection(self):
        if self.url[:2] == "ws":
            return Websocket(self.url, **self._kwargs)
        elif self.url[:4] == "http":
            return Http(self.url, **self._kwargs)
        else:
            raise ValueError("Only support http(s) and ws(s) connections!")

    @property
    def chain_params(self):
        return self.get_network()

    def get_network(self):
        return self._chain_props

    async def cache_chain_properties(self):
        """ Cache chain properties to prevent turning lots of methods into async
        """
        self._chain_props = await self.get_chain_properties()

    def get_cached_chain_properties(self):
        return self._chain_props

    async def connect(self):
        try:
            await self.connection.connect()
        except Exception as e:
            log.warning(str(e))
            self.error_url()
            await self.next()
        self.register_apis()
        await self.cache_chain_properties()

    async def disconnect(self):
        await self.connection.disconnect()

    async def next(self):
        await self.connection.disconnect()
        self.url = await self.find_next()
        await self.connect()

    async def find_next(self):
        """ Find the next url in the list
        """
        if int(self.num_retries) < 0:  # pragma: no cover
            self._cnt_retries += 1
            sleeptime = (self._cnt_retries - 1) * 2 if self._cnt_retries < 10 else 10
            if sleeptime:
                log.warning(
                    "Lost connection to node during rpcexec(): %s (%d/%d) "
                    % (self.url, self._cnt_retries, self.num_retries)
                    + "Retrying in %d seconds" % sleeptime
                )
                await asyncio.sleep(sleeptime)
            return next(self.urls)

        urls = [
            k
            for k, v in self._url_counter.items()
            if (
                # Only provide URLS if num_retries is bigger equal 0,
                # i.e. we want to do reconnects at all
                int(self.num_retries) >= 0
                # the counter for this host/endpoint should be smaller than
                # num_retries
                and v <= self.num_retries
                # let's not retry with the same URL *if* we have others
                # available
                and (k != self.url or len(self._url_counter) == 1)
            )
        ]
        if not len(urls):
            raise NumRetriesReached
        url = urls[0]
        return url
