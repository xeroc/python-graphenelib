# -*- coding: utf-8 -*-
import unittest
from .fixtures import fixture_data, Account, AccountUpdate, getOperationNameForId
from graphenecommon.exceptions import AccountDoesNotExistsException


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
        for h in account.history(limit=1, first=-1):
            pass
        for h in account.history(
            limit=1, first=2, exclude_ops=["newdemooepration"], only_ops=["fups"]
        ):
            pass
        self.assertIsInstance(Account(account), Account)

        self.assertFalse(account.is_ltm)

    def test_balances(self):
        account = Account("init0", full=True)
        balances = account.balances
        self.assertEqual(len(balances), 1)
        self.assertEqual(float(balances[0]), 1.32442)
        self.assertEqual(str(balances[0]), "1.32442 GPH")

        balance = account.balance("GPH")
        self.assertEqual(float(balance), 1.32442)
        self.assertEqual(str(balance), "1.32442 GPH")

        balance = account.balance(dict(symbol="GPH"))
        self.assertEqual(float(balance), 1.32442)
        self.assertEqual(str(balance), "1.32442 GPH")

        balance = account.balance(dict(symbol="USD"))
        self.assertEqual(float(balance), 0)
        self.assertEqual(str(balance), "0.0000 USD")

    def test_history(self):
        account = Account("init0", full=True)
        for h in account.history():
            break

    def test_account_refresh(self):
        account = Account("1.2.100")
        account.refresh()

    def test_fail_lookup_name(self):
        with self.assertRaises(AccountDoesNotExistsException):
            account = Account("sf332sas")
            account.refresh()

        with self.assertRaises(AccountDoesNotExistsException):
            account = Account("1.2.100", full=True)
            account.refresh()

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

        update = AccountUpdate("1.2.100")
        self.assertEqual(update["owner"], "1.2.100")
        self.assertIsInstance(update.account, Account)
