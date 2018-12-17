# -*- coding: utf-8 -*-
import unittest
from graphenecommon.exceptions import AssetDoesNotExistsException
from .fixtures import fixture_data, Asset


class Testcases(unittest.TestCase):
    def setUp(self):
        fixture_data()

    def test_assert(self):
        with self.assertRaises(AssetDoesNotExistsException):
            Asset("FOObarNonExisting", full=False)

    def test_full(self):
        asset = Asset("1.3.0", full=True)
        self.assertIn("dynamic_asset_data", asset)
        self.assertIn("flags", asset)
        self.assertIn("permissions", asset)
        self.assertIsInstance(asset["flags"], dict)
        self.assertIsInstance(asset["permissions"], dict)

    def test_properties(self):
        asset = Asset("1.3.0", full=False)
        self.assertIsInstance(asset.symbol, str)
        self.assertIsInstance(asset.precision, int)
        self.assertIsInstance(asset.is_bitasset, bool)
        self.assertIsInstance(asset.permissions, dict)
        self.assertEqual(asset.permissions, asset["permissions"])
        self.assertIsInstance(asset.flags, dict)
        self.assertEqual(asset.flags, asset["flags"])
