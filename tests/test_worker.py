# -*- coding: utf-8 -*-
import unittest
from datetime import datetime
from .fixtures import fixture_data, Worker, Workers, Account
from graphenecommon import exceptions


class Testcases(unittest.TestCase):
    def setUp(self):
        fixture_data()

    def test_worker(self):
        w = Worker("1.14.139")
        self.assertIsInstance(w["work_end_date"], datetime)
        self.assertIsInstance(w["work_begin_date"], datetime)
        self.assertIsInstance(w["work_begin_date"], datetime)
        self.assertIsInstance(w["daily_pay"], int)
        self.assertIsInstance(w.account, Account)
        self.assertEqual(w.account["id"], "1.2.100")
        Worker(w)

    def test_nonexist(self):
        with self.assertRaises(exceptions.WorkerDoesNotExistsException):
            Worker("foobar")

    def test_workers(self):
        ws = Workers()
        self.assertEqual(len(ws), 2)

    def test_workers2(self):
        ws = Workers._cache["Workers"] = [dict(), dict()]
        self.assertEqual(len(ws), 2)
