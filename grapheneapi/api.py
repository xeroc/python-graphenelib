# -*- coding: utf-8 -*-
import logging
from collections import Counter
from itertools import cycle
from time import sleep
from .exceptions import RPCError, NumRetriesReached

from .websocket import Websocket
from .http import Http

log = logging.getLogger(__name__)


class Api:
    def __init__(self, urls, user=None, password=None, **kwargs):

        # Some internal variables
        self._connections = dict()
        self._url_counter = Counter()

        # Let's store user and password in kwargs as well
        self.user = user
        self.password = password
        kwargs.update(dict(user=user, password=password))
        self._kwargs = kwargs

        # How often do we accept retries?
        self.num_retries = kwargs.pop("num_retries", 1)

        if not isinstance(urls, list):
            urls = [urls]

        for url in urls:
            self._url_counter[url] = 0

        self.url = urls[0]
        self._active_url = None

        # Let's also be able to deal with infinite connection
        self.urls = cycle(urls)
        self._cnt_retries = 0

        # Connect!
        self.connect()

    # Get chain parameters
    @property
    def chain_params(self):
        return self.get_network()

    def get_network(self):
        return self.get_chain_properties()

    def updated_connection(self):
        if self.url[:2] == "ws":
            return Websocket(self.url, **self._kwargs)
        elif self.url[:4] == "http":
            return Http(self.url, **self._kwargs)
        else:
            raise ValueError("Only support http(s) and ws(s) connections!")

    @property
    def connection(self):
        if self._active_url != self.url:
            log.debug(
                "Updating connection from {} to {}".format(self._active_url, self.url)
            )
            self._active_connection = self.updated_connection()
            self._active_url = self.url
        return self._active_connection

    def connect(self):
        try:
            self.connection.connect()
        except Exception as e:
            log.warning(str(e))
            self.error_url()
            self.next()
        self.register_apis()

    def find_next(self):
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
                sleep(sleeptime)
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

    def reset_counter(self):
        """ reset the failed connection counters
        """
        self._cnt_retries = 0
        for i in self._url_counter:
            self._url_counter[i] = 0

    def error_url(self):  # pragma: no cover
        if self.url in self._url_counter:
            self._url_counter[self.url] += 1
        else:
            self._url_counter[self.url] = 1

    def next(self):
        self.connection.disconnect()
        self.url = self.find_next()
        self.connect()

    def post_process_exception(self, exception):
        raise exception

    @property
    def api_id(self):
        """ This allows to list api_ids, if they have been registered through
            api_register() -- LEGACY

            In previous API version, one would connect and register to APIs
            like this

            .. code-block:: python

                self.api_id["database"] = self.database(api_id=1)
                self.api_id["history"] = self.history(api_id=1)
                self.api_id["network_broadcast"] = self.network_broadcast(
                    api_id=1)

        """
        return self.connection.api_id

    def register_apis(self):  # pragma: no cover
        """ This method is called right after connection and has previously
            been used to register to different APIs within the backend that are
            considered default. The requirement to register to APIs has been
            removed in some systems.
        """
        pass

    def __getattr__(self, name):
        def func(*args, **kwargs):
            while True:
                try:
                    func = self.connection.__getattr__(name)
                    r = func(*args, **kwargs)
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
