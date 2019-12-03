# -*- coding: utf-8 -*-
import pytest
import asyncio
import logging

from grapheneapi.aio.websocket import Websocket
from grapheneapi.aio.http import Http
from grapheneapi.aio.api import Api

logger = logging.getLogger("grapheneapi.aio")
logger.setLevel(logging.DEBUG)

logger = logging.getLogger("websockets")
logger.setLevel(logging.DEBUG)

NODE_WS = "wss://eu.nodes.bitshares.ws"
NODE_HTTPS = "https://eu.nodes.bitshares.ws"


@pytest.mark.asyncio
async def test_loop(event_loop):
    await asyncio.sleep(1)


@pytest.mark.asyncio
async def test_websocket_rpc(event_loop):
    ws = Websocket(NODE_WS, loop=event_loop)
    props = await ws.get_dynamic_global_properties()
    logger.info(props)
    await ws.disconnect()
    assert isinstance(props, dict)
    assert props["head_block_number"] > 0


@pytest.mark.asyncio
async def test_http_rpc(event_loop):
    http = Http(NODE_HTTPS, loop=event_loop)
    props = await http.get_dynamic_global_properties()
    logger.info(props)
    await http.disconnect()
    assert isinstance(props, dict)
    assert props["head_block_number"] > 0


@pytest.mark.asyncio
async def test_api_via_websocket_rpc(event_loop):
    api = Api(NODE_WS, loop=event_loop)
    await api.connect()
    props = await api.get_dynamic_global_properties()
    logger.info(props)
    config = await api.get_config()
    logger.info(config)
    await api.disconnect()
    assert isinstance(props, dict)
    assert props["head_block_number"] > 0


@pytest.mark.asyncio
async def test_api_via_http_rpc(event_loop):
    api = Api(NODE_HTTPS, loop=event_loop)
    await api.connect()
    props = await api.get_dynamic_global_properties()
    logger.info(props)
    config = await api.get_config()
    logger.info(config)
    await api.disconnect()
    assert isinstance(props, dict)
    assert props["head_block_number"] > 0
