# -*- coding: utf-8 -*-
import asyncio
import unittest
from .fixtures_aio import fixture_data, Amount, Asset


class Testcases(unittest.TestCase):
    def setUp(self):
        fixture_data()
        self.loop = asyncio.get_event_loop()
        self.asset = self.loop.run_until_complete(Asset("GPH"))
        self.symbol = self.asset["symbol"]
        self.precision = self.asset["precision"]
        self.asset2 = self.loop.run_until_complete(Asset("EUR"))

    def dotest(self, ret, amount, symbol):
        self.assertEqual(float(ret), float(amount))
        self.assertEqual(ret["symbol"], symbol)
        self.assertIsInstance(ret["asset"], dict)
        self.assertIsInstance(ret["amount"], float)

    def test_init(self):
        # String init
        amount = self.loop.run_until_complete(Amount("1 {}".format(self.symbol)))
        self.dotest(amount, 1, self.symbol)

        # Amount init
        amount = self.loop.run_until_complete(Amount(amount))
        self.dotest(amount, 1, self.symbol)

        # blockchain dict init
        amount = self.loop.run_until_complete(
            Amount({"amount": 1 * 10 ** self.precision, "asset_id": self.asset["id"]})
        )
        self.dotest(amount, 1, self.symbol)

        # API dict init
        amount = self.loop.run_until_complete(
            Amount({"amount": 1.3 * 10 ** self.precision, "asset": self.asset["id"]})
        )
        self.dotest(amount, 1.3, self.symbol)

        # Asset as symbol
        amount = self.loop.run_until_complete(
            Amount(1.3, self.loop.run_until_complete(Asset("1.3.0")))
        )
        self.dotest(amount, 1.3, self.symbol)

        # Asset as symbol
        amount = self.loop.run_until_complete(Amount(1.3, self.symbol))
        self.dotest(amount, 1.3, self.symbol)

        # keyword inits
        amount = self.loop.run_until_complete(
            Amount(amount=1.3, asset=self.loop.run_until_complete(Asset("1.3.0")))
        )
        self.dotest(amount, 1.3, self.symbol)

        # keyword inits
        amount = self.loop.run_until_complete(
            Amount(amount=1.3, asset=dict(self.loop.run_until_complete(Asset("1.3.0"))))
        )
        self.dotest(amount, 1.3, self.symbol)

        # keyword inits
        amount = self.loop.run_until_complete(Amount(amount=1.3, asset=self.symbol))
        self.dotest(amount, 1.3, self.symbol)

    def test_copy(self):
        amount = self.loop.run_until_complete(Amount("1", self.symbol))
        self.dotest(self.loop.run_until_complete(amount.copy()), 1, self.symbol)

    def test_properties(self):
        amount = self.loop.run_until_complete(Amount("1", self.symbol))
        self.assertEqual(amount.amount, 1.0)
        self.assertEqual(amount.symbol, self.symbol)
        asset = self.loop.run_until_complete(amount.asset)
        self.assertIsInstance(asset, Asset)
        self.assertEqual(asset["symbol"], self.symbol)

    def test_tuple(self):
        amount = self.loop.run_until_complete(Amount("1", self.symbol))
        self.assertEqual(amount.tuple(), (1.0, self.symbol))

    def test_json(self):
        amount = self.loop.run_until_complete(Amount("1", self.symbol))
        self.assertEqual(
            amount.json(),
            {"asset_id": self.asset["id"], "amount": 1 * 10 ** self.precision},
        )

    def test_string(self):
        self.assertEqual(
            str(self.loop.run_until_complete(Amount("1", self.symbol))),
            "1.00000 {}".format(self.symbol),
        )

    def test_int(self):
        self.assertEqual(
            int(self.loop.run_until_complete(Amount("1", self.symbol))), 100000
        )

    def test_float(self):
        self.assertEqual(
            float(self.loop.run_until_complete(Amount("1", self.symbol))), 1.00000
        )

    def test_ltge(self):
        a1 = self.loop.run_until_complete(Amount(1, self.symbol))
        a2 = self.loop.run_until_complete(Amount(2, self.symbol))
        self.assertTrue(a1 < a2)
        self.assertTrue(a2 > a1)
        self.assertTrue(a2 > 1)
        self.assertTrue(a1 < 5)

    def test_leeq(self):
        a1 = self.loop.run_until_complete(Amount(1, self.symbol))
        a2 = self.loop.run_until_complete(Amount(1, self.symbol))
        self.assertTrue(a1 <= a2)
        self.assertTrue(a1 >= a2)
        self.assertTrue(a1 <= 1)
        self.assertTrue(a1 >= 1)

    def test_ne(self):
        a1 = self.loop.run_until_complete(Amount(1, self.symbol))
        a2 = self.loop.run_until_complete(Amount(2, self.symbol))
        self.assertTrue(a1 != a2)
        self.assertTrue(a1 != 5)
        a1 = self.loop.run_until_complete(Amount(1, self.symbol))
        a2 = self.loop.run_until_complete(Amount(1, self.symbol))
        self.assertTrue(a1 == a2)
        self.assertTrue(a1 == 1)
