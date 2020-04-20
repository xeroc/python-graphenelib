# -*- coding: utf-8 -*-
import asyncio
import aiounittest
from .fixtures_aio import fixture_data, Amount, Asset


class Testcases(aiounittest.AsyncTestCase):
    def setUp(self):
        fixture_data()
        # Cannot define setUp as coroutine
        loop = asyncio.get_event_loop()
        self.asset = loop.run_until_complete(Asset("GPH"))
        self.symbol = self.asset["symbol"]
        self.precision = self.asset["precision"]
        self.asset2 = loop.run_until_complete(Asset("EUR"))

    def dotest(self, ret, amount, symbol):
        self.assertEqual(float(ret), float(amount))
        self.assertEqual(ret["symbol"], symbol)
        self.assertIsInstance(ret["asset"], dict)
        self.assertIsInstance(ret["amount"], float)

    async def test_init(self):
        # String init
        amount = await Amount("1 {}".format(self.symbol))
        self.dotest(amount, 1, self.symbol)

        # Amount init
        amount = await Amount(amount)
        self.dotest(amount, 1, self.symbol)

        # blockchain dict init
        amount = await Amount(
            {"amount": 1 * 10 ** self.precision, "asset_id": self.asset["id"]}
        )
        self.dotest(amount, 1, self.symbol)

        # API dict init
        amount = await Amount(
            {"amount": 1.3 * 10 ** self.precision, "asset": self.asset["id"]}
        )
        self.dotest(amount, 1.3, self.symbol)

        # Asset as symbol
        amount = await Amount(1.3, await Asset("1.3.0"))
        self.dotest(amount, 1.3, self.symbol)

        # Asset as symbol
        amount = await Amount(1.3, self.symbol)
        self.dotest(amount, 1.3, self.symbol)

        # keyword inits
        amount = await Amount(amount=1.3, asset=await Asset("1.3.0"))
        self.dotest(amount, 1.3, self.symbol)

        # keyword inits
        amount = await Amount(amount=1.3, asset=dict(await Asset("1.3.0")))
        self.dotest(amount, 1.3, self.symbol)

        # keyword inits
        amount = await Amount(amount=1.3, asset=self.symbol)
        self.dotest(amount, 1.3, self.symbol)

    async def test_copy(self):
        amount = await Amount("1", self.symbol)
        self.dotest(await amount.copy(), 1, self.symbol)

    async def test_properties(self):
        amount = await Amount("1", self.symbol)
        self.assertEqual(amount.amount, 1.0)
        self.assertEqual(amount.symbol, self.symbol)
        asset = await amount.asset
        self.assertIsInstance(asset, Asset)
        self.assertEqual(asset["symbol"], self.symbol)

    async def test_tuple(self):
        amount = await Amount("1", self.symbol)
        self.assertEqual(amount.tuple(), (1.0, self.symbol))

    async def test_json(self):
        amount = await Amount("1", self.symbol)
        self.assertEqual(
            amount.json(),
            {"asset_id": self.asset["id"], "amount": 1 * 10 ** self.precision},
        )

    async def test_string(self):
        self.assertEqual(
            str(await Amount("1", self.symbol)), "1.00000 {}".format(self.symbol)
        )

    async def test_int(self):
        self.assertEqual(int(await Amount("1", self.symbol)), 100000)

    async def test_float(self):
        self.assertEqual(float(await Amount("1", self.symbol)), 1.00000)

    async def test_ltge(self):
        a1 = await Amount(1, self.symbol)
        a2 = await Amount(2, self.symbol)
        self.assertTrue(a1 < a2)
        self.assertTrue(a2 > a1)
        self.assertTrue(a2 > 1)
        self.assertTrue(a1 < 5)

    async def test_leeq(self):
        a1 = await Amount(1, self.symbol)
        a2 = await Amount(1, self.symbol)
        self.assertTrue(a1 <= a2)
        self.assertTrue(a1 >= a2)
        self.assertTrue(a1 <= 1)
        self.assertTrue(a1 >= 1)

    async def test_ne(self):
        a1 = await Amount(1, self.symbol)
        a2 = await Amount(2, self.symbol)
        self.assertTrue(a1 != a2)
        self.assertTrue(a1 != 5)
        a1 = await Amount(1, self.symbol)
        a2 = await Amount(1, self.symbol)
        self.assertTrue(a1 == a2)
        self.assertTrue(a1 == 1)
