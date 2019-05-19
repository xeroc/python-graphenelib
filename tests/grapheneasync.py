import pytest
import asyncio
import logging

from grapheneasync.websocket import Websocket

logger = logging.getLogger('websockets')
logger.setLevel(logging.DEBUG)


@pytest.mark.asyncio
async def test_loop(event_loop):
    await asyncio.sleep(1)


@pytest.mark.asyncio
async def test_rpc(event_loop):
    ws = Websocket('wss://eu.nodes.bitshares.ws')
    props = await ws.get_dynamic_global_properties()
    await ws.disconnect()
    logger.info(props)
    assert isinstance(props, dict)
    assert props['head_block_number'] > 0
