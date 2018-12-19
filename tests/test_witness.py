# -*- coding: utf-8 -*-
import unittest
from datetime import datetime
from .fixtures import fixture_data, Witness, Witnesses, Account
from graphenecommon import exceptions


class Testcases(unittest.TestCase):
    def setUp(self):
        fixture_data()

    def test_Witness(self):
        w = Witness("1.6.1")
        self.assertIsInstance(w.account, Account)
        self.assertEqual(w.account["id"], "1.2.101")
        Witness(w)

    """
    def test_nonexist(self):
        with self.assertRaises(exceptions.AccountDoesNotExistsException):
            Witness("foobar")

    def test_Witnesss(self):
        ws = Witnesses()
        self.assertEqual(len(ws), 2)

    def test_Witnesss2(self):
        ws = Witnesses("init0")
        self.assertEqual(len(ws), 1)
    """
