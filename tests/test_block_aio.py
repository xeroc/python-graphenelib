# -*- coding: utf-8 -*-
import aiounittest
from graphenecommon.utils import parse_time
from .fixtures_aio import fixture_data, Block, BlockHeader


class Testcases(aiounittest.AsyncTestCase):
    def setUp(self):
        fixture_data()

    async def test_block(self):
        block = await Block(1)
        self.assertEqual(block["previous"], "0000000000000000000000000000000000000000")
        self.assertEqual(block.time(), parse_time("2015-10-13T14:12:24"))

    async def test_blockheader(self):
        header = await BlockHeader(1)
        self.assertEqual(header["previous"], "0000000000000000000000000000000000000000")
        self.assertEqual(header.time(), parse_time("2015-10-13T14:12:24"))
