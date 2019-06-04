# -*- coding: utf-8 -*-
import aiounittest
from .fixtures_aio import fixture_data, Amount, Asset, Price


class Testcases(aiounittest.AsyncTestCase):
    def setUp(self):
        fixture_data()

    async def test_init(self):
        # self.assertEqual(1, 1)

        await Price("0.315 USD/GPH")
        await Price(1.0, "USD/GOLD")
        await Price(0.315, base="USD", quote="GPH")
        await Price(0.315, base=await Asset("USD"), quote=await Asset("GPH"))
        await Price(
            {
                "base": {"amount": 1, "asset_id": "1.3.0"},
                "quote": {"amount": 10, "asset_id": "1.3.8"},
            }
        )
        await Price(
            {
                "receives": {"amount": 1, "asset_id": "1.3.0"},
                "pays": {"amount": 10, "asset_id": "1.3.8"},
            },
            base_asset=await Asset("1.3.0"),
        )
        await Price(quote="10 GOLD", base="1 USD")
        await Price("10 GOLD", "1 USD")
        await Price(await Amount("10 GOLD"), await Amount("1 USD"))
