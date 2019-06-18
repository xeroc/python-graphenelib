# -*- coding: utf-8 -*-
import aiounittest
from .fixtures_aio import fixture_data, Account, AccountUpdate, getOperationNameForId
from graphenecommon.exceptions import AccountDoesNotExistsException


class Testcases(aiounittest.AsyncTestCase):
    def setUp(self):
        fixture_data()

    async def test_account(self):
        await Account("init0")
        await Account("1.2.101")
        account = await Account("init0", full=True)
        self.assertEqual(account.name, "init0")
        self.assertEqual(account["name"], account.name)
        self.assertEqual(account["id"], "1.2.100")
        self.assertEqual(str(account), "<Account init0>")
        account = await Account("1.2.100")
        self.assertEqual(str(account), "<Account 1.2.100>")
        async for h in account.history(limit=1, first=-1):
            pass
        async for h in account.history(
            limit=1, first=2, exclude_ops=["newdemooepration"], only_ops=["fups"]
        ):
            pass
        self.assertIsInstance(await Account(account), Account)

        self.assertFalse(account.is_ltm)

    async def test_balances(self):
        account = await Account("init0", full=True)
        balances = await account.balances
        self.assertEqual(len(balances), 1)
        self.assertEqual(float(balances[0]), 1.32442)
        self.assertEqual(str(balances[0]), "1.32442 GPH")

        balance = await account.balance("GPH")
        self.assertEqual(float(balance), 1.32442)
        self.assertEqual(str(balance), "1.32442 GPH")

        balance = await account.balance(dict(symbol="GPH"))
        self.assertEqual(float(balance), 1.32442)
        self.assertEqual(str(balance), "1.32442 GPH")

        balance = await account.balance(dict(symbol="USD"))
        self.assertEqual(float(balance), 0)
        self.assertEqual(str(balance), "0.0000 USD")

    async def test_history(self):
        account = await Account("init0", full=True)
        async for h in account.history():
            break

    async def test_account_refresh(self):
        account = await Account("1.2.100")
        await account.refresh()

    async def test_fail_lookup_name(self):
        with self.assertRaises(AccountDoesNotExistsException):
            account = await Account("sf332sas")
            await account.refresh()

        with self.assertRaises(AccountDoesNotExistsException):
            account = await Account("1.2.100", full=True)
            await account.refresh()

    async def test_account_upgrade(self):
        account = await Account("init0")
        await account.upgrade()

    async def test_accountupdate(self):
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
        update = await AccountUpdate(t)
        self.assertEqual(update["owner"], "1.2.100")
        self.assertIsInstance(await update.account, Account)

        update = await AccountUpdate("1.2.100")
        self.assertEqual(update["owner"], "1.2.100")
        self.assertIsInstance(await update.account, Account)
