# -*- coding: utf-8 -*-
import aiounittest
from datetime import datetime
from .fixtures_aio import fixture_data, Witness, Witnesses, Account
from graphenecommon import exceptions


class Testcases(aiounittest.AsyncTestCase):
    def setUp(self):
        fixture_data()

    async def test_Witness(self):
        w = await Witness("1.6.1")
        account = await w.account
        self.assertIsInstance(account, Account)
        self.assertEqual(account["id"], "1.2.101")
        await Witness(w)

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
