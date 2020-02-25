# -*- coding: utf-8 -*-
import logging

from graphenecommon.exceptions import KeyNotFound
from ..wallet import Wallet as SyncWallet


log = logging.getLogger(__name__)


class Wallet(SyncWallet):
    """ The wallet is meant to maintain access to private keys for
        your accounts. It either uses manually provided private keys
        or uses a SQLite database managed by storage.py.

        :param array,dict,string keys: Predefine the wif keys to shortcut the
               wallet database

        .. note:: Wallet should be instantiated synchroously e.g.

        .. code-block:: python

            w = Wallet()

        Three wallet operation modes are possible:

        * **Wallet Database**: Here, the library loads the keys from the
          locally stored wallet SQLite database (see ``storage.py``).
        * **Providing Keys**: Here, you can provide the keys for
          your accounts manually. All you need to do is add the wif
          keys for the accounts you want to use as a simple array
          using the ``keys`` parameter to your blockchain instance.
        * **Force keys**: This more is for advanced users and
          requires that you know what you are doing. Here, the
          ``keys`` parameter is a dictionary that overwrite the
          ``active``, ``owner``, ``posting`` or ``memo`` keys for
          any account. This mode is only used for *foreign*
          signatures!
    """

    async def getOwnerKeyForAccount(self, name):
        """ Obtain owner Private Key for an account from the wallet database
        """
        account = await self.rpc.get_account(name)
        for authority in account["owner"]["key_auths"]:
            key = self.getPrivateKeyForPublicKey(authority[0])
            if key:
                return key
        raise KeyNotFound

    async def getMemoKeyForAccount(self, name):
        """ Obtain owner Memo Key for an account from the wallet database
        """
        account = await self.rpc.get_account(name)
        key = self.getPrivateKeyForPublicKey(account["options"]["memo_key"])
        if key:
            return key
        return False

    async def getActiveKeyForAccount(self, name):
        """ Obtain owner Active Key for an account from the wallet database
        """
        account = await self.rpc.get_account(name)
        for authority in account["active"]["key_auths"]:
            try:
                return self.getPrivateKeyForPublicKey(authority[0])
            except Exception:
                pass
        return False

    async def getAccountsFromPublicKey(self, pub):
        """ Obtain all accounts associated with a public key
        """
        result = await self.rpc.get_key_references([str(pub)])
        names = result[0]
        return names

    async def getAccountFromPublicKey(self, pub):
        """ Obtain the first account name from public key
        """
        # FIXME, this only returns the first associated key.
        # If the key is used by multiple accounts, this
        # will surely lead to undesired behavior
        names = list(await self.getAccountsFromPublicKey(str(pub)))
        if names:
            return names[0]

    async def getAccounts(self):
        """ Return all accounts installed in the wallet database
        """
        pubkeys = self.getPublicKeys()
        accounts = []
        for pubkey in pubkeys:
            # Filter those keys not for our network
            if pubkey[: len(self.prefix)] == self.prefix:
                accounts.extend(await self.getAccountsFromPublicKey(pubkey))
        return accounts
