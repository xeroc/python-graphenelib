# -*- coding: utf-8 -*-
import os
import hashlib
import logging

from binascii import hexlify

from graphenebase import bip38
from graphenebase.aes import AESCipher

from .exceptions import WrongMasterPasswordException, WalletLocked


log = logging.getLogger(__name__)


class MasterPassword(object):
    """ The keys are encrypted with a Masterpassword that is stored in
        the configurationStore. It has a checksum to verify correctness
        of the password
        The encrypted private keys in `keys` are encrypted with a random
        **masterkey/masterpassword** that is stored in the configuration
        encrypted by the user-provided password.

        :param ConfigStore config: Configuration store to get access to the
            encrypted master password
    """

    def __init__(self, config=None, **kwargs):
        if config is None:
            raise ValueError("If using encrypted store, a config store is required!")
        self.config = config
        self.password = None
        self.decrypted_master = None
        self.config_key = "encrypted_master_password"

    @property
    def masterkey(self):
        """ Contains the **decrypted** master key
        """
        return self.decrypted_master

    def has_masterpassword(self):
        """ Tells us if the config store knows an encrypted masterpassword
        """
        return self.config_key in self.config

    def locked(self):
        """ Is the store locked. E.g. Is a valid password known that can be
            used to decrypt the master key?
        """
        return not self.unlocked()

    def unlocked(self):
        """ Is the store unlocked so that I can decrypt the content?
        """
        if self.password is not None:
            return bool(self.password)
        else:
            if (
                "UNLOCK" in os.environ
                and os.environ["UNLOCK"]
                and self.config_key in self.config
                and self.config[self.config_key]
            ):
                log.debug("Trying to use environmental " "variable to unlock wallet")
                self.unlock(os.environ.get("UNLOCK"))
                return bool(self.password)
        return False

    def lock(self):
        """ Lock the store so that we can no longer decrypt the content of the
            store
        """
        self.password = None
        self.decrypted_master = None

    def unlock(self, password):
        """ The password is used to encrypt this masterpassword. To
            decrypt the keys stored in the keys database, one must use
            BIP38, decrypt the masterpassword from the configuration
            store with the user password, and use the decrypted
            masterpassword to decrypt the BIP38 encrypted private keys
            from the keys storage!

            :param str password: Password to use for en-/de-cryption
        """
        self.password = password
        if self.config_key in self.config and self.config[self.config_key]:
            self.decryptEncryptedMaster()
        else:
            self.newMaster(password)
            self.saveEncrytpedMaster()

    def decryptEncryptedMaster(self):
        """ Decrypt the encrypted masterkey
        """
        aes = AESCipher(self.password)
        checksum, encrypted_master = self.config[self.config_key].split("$")
        try:
            decrypted_master = aes.decrypt(encrypted_master)
        except Exception:
            self.raiseWrongMasterPasswordException()
        if checksum != self.deriveChecksum(decrypted_master):
            self.raiseWrongMasterPasswordException()
        self.decrypted_master = decrypted_master

    def raiseWrongMasterPasswordException(self):
        self.password = None
        raise WrongMasterPasswordException

    def saveEncrytpedMaster(self):
        self.config[self.config_key] = self.getEncryptedMaster()

    def newMaster(self, password):
        """ Generate a new random masterkey, encrypt it with the password and
            store it in the store.

            :param str password: Password to use for en-/de-cryption
        """
        # make sure to not overwrite an existing key
        if self.config_key in self.config and self.config[self.config_key]:
            raise Exception("Storage already has a masterpassword!")

        self.decrypted_master = hexlify(os.urandom(32)).decode("ascii")

        # Encrypt and save master
        self.password = password
        self.saveEncrytpedMaster()
        return self.masterkey

    def deriveChecksum(self, s):
        """ Derive the checksum

            :param str s: Random string for which to derive the checksum
        """
        checksum = hashlib.sha256(bytes(s, "ascii")).hexdigest()
        return checksum[:4]

    def getEncryptedMaster(self):
        """ Obtain the encrypted masterkey

            .. note:: The encrypted masterkey is checksummed, so that we can
                figure out that a provided password is correct or not. The
                checksum is only 4 bytes long!
        """
        if not self.unlocked():
            raise WalletLocked
        aes = AESCipher(self.password)
        return "{}${}".format(
            self.deriveChecksum(self.masterkey), aes.encrypt(self.masterkey)
        )

    def changePassword(self, newpassword):
        """ Change the password that allows to decrypt the master key
        """
        if not self.unlocked():
            raise WalletLocked
        self.password = newpassword
        self.saveEncrytpedMaster()

    def decrypt(self, wif):
        """ Decrypt the content according to BIP38

            :param str wif: Encrypted key
        """
        if not self.unlocked():
            raise WalletLocked
        return format(bip38.decrypt(wif, self.masterkey), "wif")

    def encrypt(self, wif):
        """ Encrypt the content according to BIP38

            :param str wif: Unencrypted key
        """
        if not self.unlocked():
            raise WalletLocked
        return format(bip38.encrypt(str(wif), self.masterkey), "encwif")
