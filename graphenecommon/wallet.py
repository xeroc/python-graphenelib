# -*- coding: utf-8 -*-
import logging

from graphenestorage import InRamPlainKeyStore, SqliteEncryptedKeyStore
from graphenecommon.exceptions import (
    InvalidWifError,
    KeyAlreadyInStoreException,
    KeyNotFound,
    OfflineHasNoRPCException,
    WalletExists,
)
from .instance import AbstractBlockchainInstanceProvider


log = logging.getLogger(__name__)


class Wallet(AbstractBlockchainInstanceProvider):
    """ The wallet is meant to maintain access to private keys for
        your accounts. It either uses manually provided private keys
        or uses a SQLite database managed by storage.py.

        :param array,dict,string keys: Predefine the wif keys to shortcut the
               wallet database

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

    def __init__(self, *args, **kwargs):
        self.define_classes()
        assert self.privatekey_class
        assert self.default_key_store_app_name

        # Compatibility after name change from wif->keys
        if "wif" in kwargs and "keys" not in kwargs:
            kwargs["keys"] = kwargs["wif"]

        if "keys" in kwargs:
            self.store = InRamPlainKeyStore()
            self.setKeys(kwargs["keys"])
        else:
            if "appname" not in kwargs:
                kwargs["appname"] = self.default_key_store_app_name
            self.store = kwargs.get(
                "key_store",
                SqliteEncryptedKeyStore(config=self.blockchain.config, **kwargs),
            )

    def privatekey(self, key):
        return self.privatekey_class(key, prefix=self.prefix)

    def publickey_from_wif(self, wif):
        return str(self.privatekey(str(wif)).pubkey)

    @property
    def prefix(self):
        if self.blockchain.is_connected():
            return self.blockchain.prefix
        else:
            # If not connected, load prefix from config
            return self.blockchain.config["prefix"]

    @property
    def rpc(self):
        if not self.blockchain.is_connected():
            raise OfflineHasNoRPCException("No RPC available in offline mode!")
        return self.blockchain.rpc

    def setKeys(self, loadkeys):
        """ This method is strictly only for in memory keys that are
            passed to Wallet with the ``keys`` argument
        """
        log.debug("Force setting of private keys. Not using the wallet database!")
        if isinstance(loadkeys, dict):
            loadkeys = list(loadkeys.values())
        elif not isinstance(loadkeys, (list, set)):
            loadkeys = [loadkeys]
        for wif in loadkeys:
            pub = self.publickey_from_wif(wif)
            self.store.add(str(wif), pub)

    def is_encrypted(self):
        """ Is the key store encrypted?
        """
        return self.store.is_encrypted()

    def unlock(self, pwd):
        """ Unlock the wallet database
        """
        if self.store.is_encrypted():
            return self.store.unlock(pwd)

    def lock(self):
        """ Lock the wallet database
        """
        if self.store.is_encrypted():
            return self.store.lock()
        else:
            return False

    def unlocked(self):
        """ Is the wallet database unlocked?
        """
        if self.store.is_encrypted():
            return not self.store.locked()
        else:
            return True

    def locked(self):
        """ Is the wallet database locked?
        """
        if self.store.is_encrypted():
            return self.store.locked()

    def changePassphrase(self, new_pwd):
        """ Change the passphrase for the wallet database
        """
        self.masterpwd.changePassword(new_pwd)

    def created(self):
        """ Do we have a wallet database already?
        """
        if len(self.store.getPublicKeys()):
            # Already keys installed
            return True
        else:
            return False

    def create(self, pwd):
        """ Alias for newWallet()
        """
        self.newWallet(pwd)

    def newWallet(self, pwd):
        """ Create a new wallet database
        """
        if self.created():
            raise WalletExists("You already have created a wallet!")
        self.store.unlock(pwd)

    def addPrivateKey(self, wif):
        """ Add a private key to the wallet database
        """
        try:
            pub = self.publickey_from_wif(wif)
        except Exception:
            raise InvalidWifError("Invalid Key format!")
        if str(pub) in self.store:
            raise KeyAlreadyInStoreException("Key already in the store")
        self.store.add(str(wif), str(pub))

    def getPrivateKeyForPublicKey(self, pub):
        """ Obtain the private key for a given public key

            :param str pub: Public Key
        """
        if str(pub) not in self.store:
            raise KeyNotFound
        return self.store.getPrivateKeyForPublicKey(str(pub))

    def removePrivateKeyFromPublicKey(self, pub):
        """ Remove a key from the wallet database
        """
        self.store.delete(str(pub))

    def removeAccount(self, account):
        """ Remove all keys associated with a given account
        """
        accounts = self.getAccounts()
        for a in accounts:
            if a["name"] == account:
                self.store.delete(a["pubkey"])

    def getOwnerKeyForAccount(self, name):
        """ Obtain owner Private Key for an account from the wallet database
        """
        account = self.rpc.get_account(name)
        for authority in account["owner"]["key_auths"]:
            key = self.getPrivateKeyForPublicKey(authority[0])
            if key:
                return key
        raise KeyNotFound

    def getMemoKeyForAccount(self, name):
        """ Obtain owner Memo Key for an account from the wallet database
        """
        account = self.rpc.get_account(name)
        key = self.getPrivateKeyForPublicKey(account["options"]["memo_key"])
        if key:
            return key
        return False

    def getActiveKeyForAccount(self, name):
        """ Obtain owner Active Key for an account from the wallet database
        """
        account = self.rpc.get_account(name)
        for authority in account["active"]["key_auths"]:
            try:
                return self.getPrivateKeyForPublicKey(authority[0])
            except Exception:
                pass
        return False

    def getAccountFromPrivateKey(self, wif):
        """ Obtain account name from private key
        """
        pub = self.publickey_from_wif(wif)
        return self.getAccountFromPublicKey(pub)

    def getAccountsFromPublicKey(self, pub):
        """ Obtain all accounts associated with a public key
        """
        names = self.rpc.get_key_references([str(pub)])[0]
        for name in names:
            yield name

    def getAccountFromPublicKey(self, pub):
        """ Obtain the first account name from public key
        """
        # FIXME, this only returns the first associated key.
        # If the key is used by multiple accounts, this
        # will surely lead to undesired behavior
        names = list(self.getAccountsFromPublicKey(str(pub)))
        if names:
            return names[0]

    def getAllAccounts(self, pub):
        """ Get the account data for a public key (all accounts found for this
            public key)
        """
        return DeprecationWarning(
            "Use 'getAccountsFromPublicKey' instead and resolve with your own "
            "Account() class!"
        )

    def getKeyType(self, account, pub):
        """ Get key type
        """
        for authority in ["owner", "active"]:
            for key in account[authority]["key_auths"]:
                if str(pub) == key[0]:
                    return authority
        if str(pub) == account["options"]["memo_key"]:
            return "memo"
        return None

    def getAccounts(self):
        """ Return all accounts installed in the wallet database
        """
        pubkeys = self.getPublicKeys()
        accounts = []
        for pubkey in pubkeys:
            # Filter those keys not for our network
            if pubkey[: len(self.prefix)] == self.prefix:
                accounts.extend(self.getAccountsFromPublicKey(pubkey))
        return accounts

    def getPublicKeys(self, current=False):
        """ Return all installed public keys

            :param bool current: If true, returns only keys for currently
                connected blockchain
        """
        pubkeys = self.store.getPublicKeys()
        if not current:
            return pubkeys
        pubs = []
        for pubkey in pubkeys:
            # Filter those keys not for our network
            if pubkey[: len(self.prefix)] == self.prefix:
                pubs.append(pubkey)
        return pubs

    def wipe(self, sure=False):
        if not sure:
            log.error(
                "You need to confirm that you are sure "
                "and understand the implications of "
                "wiping your wallet!"
            )
            return
        else:
            self.store.wipe()
