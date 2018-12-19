# -*- coding: utf-8 -*-
import unittest
from .fixtures import fixture_data, Witnesses


class Testcases(unittest.TestCase):
    def setUp(self):
        fixture_data()

    def test_witnesses(self):
        Witnesses._cache["Witnesses"] = [dict(id="1.6.0", witness_account="init0")]
        w = Witnesses()
        self.assertIn("1.6.0", w)
        Witnesses.clear_cache()
        self.assertFalse(Witnesses())
