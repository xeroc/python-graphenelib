# -*- coding: utf-8 -*-
import unittest
from .fixtures import fixture_data, Account, AccountUpdate, getOperationNameForId


class Testcases(unittest.TestCase):
    def setUp(self):
        fixture_data()

    def test_account(self):
        Account("init0")
        Account("1.2.101")
        account = Account("init0", full=True)
        self.assertEqual(account.name, "init0")
        self.assertEqual(account["name"], account.name)
        self.assertEqual(account["id"], "1.2.100")
        self.assertEqual(str(account), "<Account init0>")
        account = Account("1.2.100")
        self.assertEqual(str(account), "<Account 1.2.100>")
        for h in account.history(limit=1):
            pass
        self.assertIsInstance(Account(account), Account)

    def test_account_upgrade(self):
        account = Account("init0")
        account.upgrade()

    def test_accountupdate(self):
        t = {
            "id": "2.6.29",
            "lifetime_fees_paid": "44261516129",
            "most_recent_op": "2.9.0",
            "owner": "1.2.100",
            "pending_fees": 0,
            "pending_vested_fees": 16310,
            "total_core_in_orders": "6788845277634",
            "total_ops": 0,
        }
        update = AccountUpdate(t)
        self.assertEqual(update["owner"], "1.2.100")
        self.assertIsInstance(update.account, Account)
