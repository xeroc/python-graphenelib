# -*- coding: utf-8 -*-
import aiounittest
from graphenecommon.exceptions import AssetDoesNotExistsException
from .fixtures_aio import fixture_data, Asset


class Testcases(aiounittest.AsyncTestCase):
    def setUp(self):
        fixture_data()

    async def test_assert(self):
        with self.assertRaises(AssetDoesNotExistsException):
            await Asset("FOObarNonExisting", full=False)

    async def test_full(self):
        asset = await Asset("1.3.0", full=True)
        self.assertIn("dynamic_asset_data", asset)
        self.assertIn("flags", asset)
        self.assertIn("permissions", asset)
        self.assertIsInstance(asset["flags"], dict)
        self.assertIsInstance(asset["permissions"], dict)

    async def test_properties(self):
        asset = await Asset("1.3.0", full=False)
        self.assertIsInstance(asset.symbol, str)
        self.assertIsInstance(asset.precision, int)
        self.assertIsInstance(asset.is_bitasset, bool)
        self.assertIsInstance(asset.permissions, dict)
        self.assertEqual(asset.permissions, asset["permissions"])
        self.assertIsInstance(asset.flags, dict)
        self.assertEqual(asset.flags, asset["flags"])

    async def test_refresh(self):
        asset = await Asset("1.3.0", full=False)
        await asset.refresh()
        self.assertIn("flags", asset)
