Asyncio support
===============

The library has full support of asyncio, though you need to be aware it has some limitations.

Example
-------

A very basic example on how to do raw API call:

.. code-block:: python

    import asyncio
    from grapheneapi.aio.websocket import Websocket

    import logging
    logger = logging.getLogger('websockets')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

    loop = asyncio.get_event_loop()
    ws = Websocket('wss://eu.nodes.bitshares.ws', loop=loop)
    props = loop.run_until_complete(ws.get_dynamic_global_properties())
    print(props)

Limitations
-----------

* Most of the classes requires async init because during instantiation some API calls has to be performed:

.. code-block:: python

    await Amount('10 FOO')

* Several math operations are not available for :class:`graphenecommon.aio.Amount`, :class:`graphenecommon.aio.Price`
  objects. This includes multiplication, division etc. This limitation is due to unability to define python magic
  methods (``__mul__``, ``__div__``, etc) as async coroutines

Concurrent RPC calls
--------------------

When using async version, you can perform multiple RPC calls from different coroutines concurrently. The library will
send requests immediately in non-blocking manner. Incoming responses will be properly matched with queries by using "id"
field of json-rpc query.

Subscriptions
-------------

In asyncio version subscription notifications are not handled in callback-based manner. Instead, they are available in
`self.notifications` queue which is :class:`asyncio.Queue`.

Debugging
---------

To enable debugging on RPC level, you can raise loglevel on following loggers (don't forget to set formatter as well):

.. code-block:: python

    log = logging.getLogger("websockets")
    log.setLevel(logging.DEBUG)

    log = logging.getLogger("grapheneapi")
    log.setLevel(logging.DEBUG)

Tests
-----

Current testsuite uses pre-populated object cache, so it doesn't cover lots of functionality. Asyncio-specific tests
could be run via ``pytest -v tests/test_*aio*.py``
