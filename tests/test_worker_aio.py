# -*- coding: utf-8 -*-
import aiounittest
from datetime import datetime
from .fixtures_aio import fixture_data, Worker, Workers, Account
from graphenecommon import exceptions


class Testcases(aiounittest.AsyncTestCase):
    def setUp(self):
        fixture_data()

    async def test_worker(self):
        w = await Worker("1.14.139")
        self.assertIsInstance(w["work_end_date"], datetime)
        self.assertIsInstance(w["work_begin_date"], datetime)
        self.assertIsInstance(w["work_begin_date"], datetime)
        self.assertIsInstance(w["daily_pay"], int)
        account = await w.account
        self.assertIsInstance(account, Account)
        self.assertEqual(account["id"], "1.2.100")
        await Worker(w)

    async def test_nonexist(self):
        with self.assertRaises(exceptions.WorkerDoesNotExistsException):
            await Worker("foobar")

    async def test_workers(self):
        ws = await Workers()
        self.assertEqual(len(ws), 2)
