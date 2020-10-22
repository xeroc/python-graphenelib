# -*- coding: utf-8 -*-
import logging

from asyncinit import asyncinit

from .blockchainobject import BlockchainObject
from ..exceptions import AccountDoesNotExistsException
from ..account import Account as SyncAccount, AccountUpdate as SyncAccountUpdate


log = logging.getLogger()


class Account(BlockchainObject, SyncAccount):
    """ This class allows to easily access Account data

        :param str account_name: Name of the account
        :param instance blockchain_instance: instance to use when accesing a RPC
        :param bool full: Obtain all account data including orders, positions, etc.
        :param bool lazy: Use lazy loading
        :param bool full: Obtain all account data including orders, positions,
               etc.
        :returns: Account data
        :rtype: dictionary
        :raises .exceptions.AccountDoesNotExistsException: if account
                does not exist

        Instances of this class are dictionaries that come with additional
        methods (see below) that allow dealing with an account and it's
        corresponding functions.

        .. code-block:: python

            from aio.account import Account
            account = await Account("init0")
            print(account)

        .. note:: This class comes with its own caching function to reduce the
                  load on the API server. Instances of this class can be
                  refreshed with ``await Account.refresh()``.

    """

    async def __init__(self, *args, **kwargs):
        self.define_classes()
        assert self.type_id
        assert self.amount_class
        assert self.operations

        self.full = kwargs.pop("full", False)
        await BlockchainObject.__init__(self, *args, **kwargs)

    async def refresh(self):
        """ Refresh/Obtain an account's data from the API server
        """
        import re

        if re.match(r"^1\.2\.[0-9]*$", self.identifier):
            result = await self.blockchain.rpc.get_objects([self.identifier])
            account = result[0]
        else:
            result = await self.blockchain.rpc.lookup_account_names([self.identifier])
            account = result[0]
        if not account:
            raise AccountDoesNotExistsException(self.identifier)
        self.store(account, account["name"])
        self.store(account, account["id"])

        if self.full:  # pragma: no cover
            accounts = await self.blockchain.rpc.get_full_accounts(
                [account["id"]], False
            )
            if accounts and isinstance(accounts, list):
                account = accounts[0][1]
            else:
                raise AccountDoesNotExistsException(self.identifier)
            await super(Account, self).__init__(
                account["account"], blockchain_instance=self.blockchain
            )
            for k, v in account.items():
                if k != "account":
                    self[k] = v
        else:
            await super(Account, self).__init__(
                account, blockchain_instance=self.blockchain
            )

    async def ensure_full(self):  # pragma: no cover
        if not self.is_fully_loaded:
            self.full = True
            await self.refresh()

    @property
    async def balances(self):
        """ List balances of an account. This call returns instances of
            :class:`amount.Amount`.
        """
        balances = await self.blockchain.rpc.get_account_balances(self["id"], [])
        return [
            await self.amount_class(b, blockchain_instance=self.blockchain)
            for b in balances
            if int(b["amount"]) > 0
        ]

    async def balance(self, symbol):
        """ Obtain the balance of a specific Asset. This call returns instances of
            :class:`amount.Amount`.
        """
        if isinstance(symbol, dict) and "symbol" in symbol:
            symbol = symbol["symbol"]
        balances = await self.balances
        for b in balances:
            if b["symbol"] == symbol:
                return b
        return await self.amount_class(0, symbol, blockchain_instance=self.blockchain)

    async def history(self, first=0, last=0, limit=-1, only_ops=[], exclude_ops=[]):
        """ Returns a generator for individual account transactions. The
            latest operation will be first. This call can be used in a
            ``for`` loop.

            :param int first: sequence number of the first
                transaction to return (*optional*)
            :param int last: sequence number of the last
                transaction to return (*optional*)
            :param int limit: limit number of transactions to
                return (*optional*)
            :param array only_ops: Limit generator by these
                operations (*optional*)
            :param array exclude_ops: Exclude these operations from
                generator (*optional*).

            ... note::
                only_ops and exclude_ops takes an array of strings:
                The full list of operation ID's can be found in
                operationids.py.
                Example: ['transfer', 'fill_order']
        """
        _limit = 100
        cnt = 0

        if first < 0:
            first = 0

        while True:
            # RPC call
            txs = await self.blockchain.rpc.get_account_history(
                self["id"],
                "1.11.{}".format(last),
                _limit,
                "1.11.{}".format(first - 1),
                api="history",
            )
            for i in txs:
                if (
                    exclude_ops
                    and self.operations.getOperationNameForId(i["op"][0]) in exclude_ops
                ):
                    continue
                if (
                    not only_ops
                    or self.operations.getOperationNameForId(i["op"][0]) in only_ops
                ):
                    cnt += 1
                    yield i
                    if limit >= 0 and cnt >= limit:  # pragma: no cover
                        return

            if not txs:
                log.info("No more history returned from API node")
                break
            if len(txs) < _limit:
                log.info("Less than {} have been returned.".format(_limit))
                break
            first = int(txs[-1]["id"].split(".")[2])

    async def upgrade(self):  # pragma: no cover
        """ Upgrade account to life time member
        """
        assert callable(self.blockchain.upgrade_account)
        return await self.blockchain.upgrade_account(account=self)

    async def whitelist(self, account):  # pragma: no cover
        """ Add an other account to the whitelist of this account
        """
        assert callable(self.blockchain.account_whitelist)
        return await self.blockchain.account_whitelist(
            account, lists=["white"], account=self
        )

    async def blacklist(self, account):  # pragma: no cover
        """ Add an other account to the blacklist of this account
        """
        assert callable(self.blockchain.account_whitelist)
        return await self.blockchain.account_whitelist(
            account, lists=["black"], account=self
        )

    async def nolist(self, account):  # pragma: no cover
        """ Remove an other account from any list of this account
        """
        assert callable(self.blockchain.account_whitelist)
        return await self.blockchain.account_whitelist(account, lists=[], account=self)


@asyncinit
class AccountUpdate(SyncAccountUpdate):
    """ This purpose of this class is to keep track of account updates
        as they are pushed through by :class:`notify.Notify`.

        Instances of this class are dictionaries and take the following
        form:

        ... code-block: js

            {'id': '2.6.29',
             'lifetime_fees_paid': '44261516129',
             'most_recent_op': '2.9.0',
             'owner': '1.2.29',
             'pending_fees': 0,
             'pending_vested_fees': 16310,
             'total_core_in_orders': '6788845277634',
             'total_ops': 0}

    """

    async def __init__(self, data, *args, **kwargs):
        self.define_classes()
        assert self.account_class
        if isinstance(data, dict):
            super(AccountUpdate, self).__init__(data)
        else:
            account = await self.account_class(
                data, blockchain_instance=self.blockchain
            )
            result = await self.blockchain.rpc.get_objects(
                ["2.6.%s" % (account["id"].split(".")[2])]
            )
            update = result[0]
            super(AccountUpdate, self).__init__(update)

    @property
    async def account(self):
        """ In oder to obtain the actual
            :class:`account.Account` from this class, you can
            use the ``account`` attribute.
        """
        account = await self.account_class(
            self["owner"], blockchain_instance=self.blockchain
        )
        # account.refresh()
        return account
