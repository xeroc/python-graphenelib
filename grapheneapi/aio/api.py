# -*- coding: utf-8 -*-
import asyncio
import logging
from grapheneapi.exceptions import NumRetriesReached, RPCError

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

    def __getattr__(self, name):
        async def func(*args, **kwargs):
            while True:
                try:
                    func = self.connection.__getattr__(name)
                    r = await func(*args, **kwargs)
                    self.reset_counter()
                    break
                except KeyboardInterrupt:  # pragma: no cover
                    raise
                except RPCError as e:  # pragma: no cover
                    """ When the backend actual returns an error
                    """
                    self.post_process_exception(e)
                    # the above line should raise. Let's be sure to at least
                    # break
                    break  # pragma: no cover
                except IOError:  # pragma: no cover
                    import traceback

                    log.debug(traceback.format_exc())
                    log.warning("Connection was closed remotely.")
                    log.warning("Reconnecting ...")
                    self.error_url()
                    self.next()
                except Exception as e:  # pragma: no cover
                    """ When something fails talking to the backend
                    """
                    import traceback

                    log.debug(traceback.format_exc())
                    log.warning(str(e))
                    log.warning("Reconnecting ...")
                    self.error_url()
                    self.next()

            return r

        return func
