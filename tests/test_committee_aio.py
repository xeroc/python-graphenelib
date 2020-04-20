# -*- coding: utf-8 -*-
import aiounittest
from graphenecommon import exceptions
from .fixtures_aio import fixture_data, Account, Committee


class Testcases(aiounittest.AsyncTestCase):
    def setUp(self):
        fixture_data()

    async def test_Committee(self):
        with self.assertRaises(exceptions.AccountDoesNotExistsException):
            await Committee("FOObarNonExisting")

        c = await Committee("1.5.0")
        self.assertEqual(c["id"], "1.5.0")
        self.assertIsInstance(await c.account, Account)

        with self.assertRaises(exceptions.CommitteeMemberDoesNotExistsException):
            await Committee("1.5.1")
