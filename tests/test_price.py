# -*- coding: utf-8 -*-
from .fixtures import fixture_data, Amount, Asset, Price
import unittest


class Testcases(unittest.TestCase):
    def setUp(self):
        fixture_data()

    def test_init(self):
        # self.assertEqual(1, 1)

        Price("0.315 USD/GPH")
        Price(1.0, "USD/GOLD")
        Price(0.315, base="USD", quote="GPH")
        Price(0.315, base=Asset("USD"), quote=Asset("GPH"))
        Price(
            {
                "base": {"amount": 1, "asset_id": "1.3.0"},
                "quote": {"amount": 10, "asset_id": "1.3.8"},
            }
        )
        Price(
            {
                "receives": {"amount": 1, "asset_id": "1.3.0"},
                "pays": {"amount": 10, "asset_id": "1.3.8"},
            },
            base_asset=Asset("1.3.0"),
        )
        Price(quote="10 GOLD", base="1 USD")
        Price("10 GOLD", "1 USD")
        Price(Amount("10 GOLD"), Amount("1 USD"))

    def test_multiplication(self):
        p1 = Price(10.0, "USD/GOLD")
        p2 = Price(5.0, "EUR/USD")
        p3 = p1 * p2
        p4 = p3.as_base("GOLD")

        self.assertEqual(p4["quote"]["symbol"], "EUR")
        self.assertEqual(p4["base"]["symbol"], "GOLD")
        # 10 USD/GOLD * 0.2 EUR/USD = 50 EUR/GOLD = 0.02 GOLD/EUR
        self.assertEqual(float(p4), 0.02)

        # Inline multiplication
        p5 = p1
        p5 *= p2
        p4 = p5.as_base("GOLD")
        self.assertEqual(p4["quote"]["symbol"], "EUR")
        self.assertEqual(p4["base"]["symbol"], "GOLD")
        # 10 USD/GOLD * 0.2 EUR/USD = 2 EUR/GOLD = 0.02 GOLD/EUR
        self.assertEqual(float(p4), 0.02)

    def test_div(self):
        p1 = Price(10.0, "USD/GOLD")
        p2 = Price(5.0, "USD/EUR")

        # 10 USD/GOLD / 5 USD/EUR = 2 EUR/GOLD
        p3 = p1 / p2
        p4 = p3.as_base("EUR")
        self.assertEqual(p4["base"]["symbol"], "EUR")
        self.assertEqual(p4["quote"]["symbol"], "GOLD")
        # 10 USD/GOLD * 0.2 EUR/USD = 2 EUR/GOLD = 0.5 GOLD/EUR
        self.assertEqual(float(p4), 2)

    def test_div2(self):
        p1 = Price(10.0, "USD/GOLD")
        p2 = Price(5.0, "USD/GOLD")

        # 10 USD/GOLD / 5 USD/EUR = 2 EUR/GOLD
        p3 = p1 / p2
        self.assertTrue(isinstance(p3, (float, int)))
        self.assertEqual(float(p3), 2.0)
