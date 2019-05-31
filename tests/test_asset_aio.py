# -*- coding: utf-8 -*-
import unittest
import asyncio
from graphenecommon.exceptions import AssetDoesNotExistsException
from .fixtures_aio import fixture_data, Asset


class Testcases(unittest.TestCase):
    def setUp(self):
        fixture_data()
        self.loop = asyncio.get_event_loop()

    def test_assert(self):
        with self.assertRaises(AssetDoesNotExistsException):
            self.loop.run_until_complete(Asset("FOObarNonExisting", full=False))

    def test_full(self):
        asset = self.loop.run_until_complete(Asset("1.3.0", full=True))
        self.assertIn("dynamic_asset_data", asset)
        self.assertIn("flags", asset)
        self.assertIn("permissions", asset)
        self.assertIsInstance(asset["flags"], dict)
        self.assertIsInstance(asset["permissions"], dict)

    def test_properties(self):
        asset = self.loop.run_until_complete(Asset("1.3.0", full=False))
        self.assertIsInstance(asset.symbol, str)
        self.assertIsInstance(asset.precision, int)
        self.assertIsInstance(asset.is_bitasset, bool)
        self.assertIsInstance(asset.permissions, dict)
        self.assertEqual(asset.permissions, asset["permissions"])
        self.assertIsInstance(asset.flags, dict)
        self.assertEqual(asset.flags, asset["flags"])

    def test_refresh(self):
        asset = self.loop.run_until_complete(Asset("1.3.0", full=False))
        self.loop.run_until_complete(asset.refresh())
        self.assertIn("flags", asset)
