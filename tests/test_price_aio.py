# -*- coding: utf-8 -*-
from .fixtures_aio import fixture_data, Amount, Asset, Price
import asyncio
import unittest


class Testcases(unittest.TestCase):
    def setUp(self):
        fixture_data()
        self.loop = asyncio.get_event_loop()

    def test_init(self):
        # self.assertEqual(1, 1)

        self.loop.run_until_complete(Price("0.315 USD/GPH"))
        self.loop.run_until_complete(Price(1.0, "USD/GOLD"))
        self.loop.run_until_complete(Price(0.315, base="USD", quote="GPH"))
        self.loop.run_until_complete(
            Price(
                0.315,
                base=self.loop.run_until_complete(Asset("USD")),
                quote=self.loop.run_until_complete(Asset("GPH")),
            )
        )
        self.loop.run_until_complete(
            Price(
                {
                    "base": {"amount": 1, "asset_id": "1.3.0"},
                    "quote": {"amount": 10, "asset_id": "1.3.8"},
                }
            )
        )
        self.loop.run_until_complete(
            Price(
                {
                    "receives": {"amount": 1, "asset_id": "1.3.0"},
                    "pays": {"amount": 10, "asset_id": "1.3.8"},
                },
                base_asset=self.loop.run_until_complete(Asset("1.3.0")),
            )
        )
        self.loop.run_until_complete(Price(quote="10 GOLD", base="1 USD"))
        self.loop.run_until_complete(Price("10 GOLD", "1 USD"))
        self.loop.run_until_complete(
            Price(
                self.loop.run_until_complete(Amount("10 GOLD")),
                self.loop.run_until_complete(Amount("1 USD")),
            )
        )
