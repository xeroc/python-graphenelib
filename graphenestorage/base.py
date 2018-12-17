# -*- coding: utf-8 -*-
import logging

from .masterpassword import MasterPassword
from .interfaces import KeyInterface, ConfigInterface, EncryptedKeyInterface
from .ram import InRamStore
from .sqlite import SQLiteStore
from .exceptions import KeyAlreadyInStoreException

log = logging.getLogger(__name__)


# Configuration
class InRamConfigurationStore(InRamStore, ConfigInterface):
    """ A simple example that stores configuration in RAM.

        Internally, this works by simply inheriting
        :class:`graphenestorage.ram.InRamStore`. The interface is defined in
        :class:`graphenestorage.interfaces.ConfigInterface`.
    """

    pass


class SqliteConfigurationStore(SQLiteStore, ConfigInterface):
    """ This is the configuration storage that stores key/value
        pairs in the `config` table of the SQLite3 database.

        Internally, this works by simply inheriting
        :class:`graphenestorage.sqlite.SQLiteStore`. The interface is defined
        in :class:`graphenestorage.interfaces.ConfigInterface`.
    """

    #: The table name for the configuration
    __tablename__ = "config"
    #: The name of the 'key' column
    __key__ = "key"
    #: The name of the 'value' column
    __value__ = "value"


# Keys
class InRamPlainKeyStore(InRamStore, KeyInterface):
    """ A simple in-RAM Store that stores keys unencrypted in RAM

        Internally, this works by simply inheriting
        :class:`graphenestorage.ram.InRamStore`. The interface is defined in
        :class:`graphenestorage.interfaces.KeyInterface`.
    """

    def getPublicKeys(self):
        return [k for k, v in self.items()]

    def getPrivateKeyForPublicKey(self, pub):
        return self.get(str(pub), None)

    def add(self, wif, pub):
        if str(pub) in self:
            raise KeyAlreadyInStoreException
        self[str(pub)] = str(wif)

    def delete(self, pub):
        InRamStore.delete(self, str(pub))


class SqlitePlainKeyStore(SQLiteStore, KeyInterface):
    """ This is the key storage that stores the public key and the
        **unencrypted** private key in the `keys` table in the SQLite3
        database.

        Internally, this works by simply inheriting
        :class:`graphenestorage.ram.InRamStore`. The interface is defined in
        :class:`graphenestorage.interfaces.KeyInterface`.
    """

    #: The table name for the configuration
    __tablename__ = "keys"
    #: The name of the 'key' column
    __key__ = "pub"
    #: The name of the 'value' column
    __value__ = "wif"

    def getPublicKeys(self):
        return [k for k, v in self.items()]

    def getPrivateKeyForPublicKey(self, pub):
        return self[pub]

    def add(self, wif, pub):
        if str(pub) in self:
            raise KeyAlreadyInStoreException
        self[str(pub)] = str(wif)

    def delete(self, pub):
        SQLiteStore.delete(self, str(pub))

    def is_encrypted(self):
        """ Returns False, as we are not encrypted here
        """
        return False


class KeyEncryption(MasterPassword, EncryptedKeyInterface):
    """ This is an interface class that provides the methods required for
        EncryptedKeyInterface and links them to the MasterPassword-provided
        functionatlity, accordingly.
    """

    def __init__(self, *args, **kwargs):
        EncryptedKeyInterface.__init__(self, *args, **kwargs)
        MasterPassword.__init__(self, *args, **kwargs)

    # Interface to deal with encrypted keys
    def getPublicKeys(self):
        return [k for k, v in self.items()]

    def getPrivateKeyForPublicKey(self, pub):
        wif = self.get(str(pub), None)
        if wif:
            return self.decrypt(wif)  # From Masterpassword

    def add(self, wif, pub):
        if str(pub) in self:
            raise KeyAlreadyInStoreException
        self[str(pub)] = self.encrypt(str(wif))  # From Masterpassword

    def is_encrypted(self):
        return True


class InRamEncryptedKeyStore(InRamStore, KeyEncryption):
    """ An in-RAM Store that stores keys **encrypted** in RAM.

        Internally, this works by simply inheriting
        :class:`graphenestorage.ram.InRamStore`. The interface is defined in
        :class:`graphenestorage.interfaces.KeyInterface`.

        .. note:: This module also inherits
            :class:`graphenestorage.masterpassword.MasterPassword` which offers
            additional methods and deals with encrypting the keys.
    """

    def __init__(self, *args, **kwargs):
        InRamStore.__init__(self, *args, **kwargs)
        KeyEncryption.__init__(self, *args, **kwargs)


class SqliteEncryptedKeyStore(SQLiteStore, KeyEncryption):
    """ This is the key storage that stores the public key and the
        **encrypted** private key in the `keys` table in the SQLite3 database.

        Internally, this works by simply inheriting
        :class:`graphenestorage.ram.InRamStore`. The interface is defined in
        :class:`graphenestorage.interfaces.KeyInterface`.

        .. note:: This module also inherits
            :class:`graphenestorage.masterpassword.MasterPassword` which offers
            additional methods and deals with encrypting the keys.
    """

    __tablename__ = "keys"
    __key__ = "pub"
    __value__ = "wif"

    def __init__(self, *args, **kwargs):
        SQLiteStore.__init__(self, *args, **kwargs)
        KeyEncryption.__init__(self, *args, **kwargs)
