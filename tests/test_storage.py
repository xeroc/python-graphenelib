# -*- coding: utf-8 -*-
import os
import unittest

from .fixtures import (
    PrivateKey,
    bip38,
    WrongMasterPasswordException,
    KeyAlreadyInStoreException,
    WalletLocked,
    storage,
    StoreInterface,
    KeyInterface,
    ConfigInterface,
    EncryptedKeyInterface,
    SQLiteStore,
)


def pubprivpair(wif):
    return (str(wif), str(PrivateKey(wif).pubkey))


class Testcases(unittest.TestCase):
    def test_interface(self):
        for k in [
            ConfigInterface(),
            KeyInterface(),
            StoreInterface(),
            EncryptedKeyInterface(),
        ]:
            k.setdefault("node", "foobar")
            assert k["node"] == "foobar"
            k["foobar"] = "value"
            k["foobar"]
            assert k["foobar"] == "value"
            self.assertIsNone(k["none"])
            iter(k)
            len(k)
            "foobar" in k
            k.items()
            k.get("foobar")
            with self.assertRaises(NotImplementedError):
                k.delete("foobar")
            with self.assertRaises(NotImplementedError):
                k.wipe()

        keys = KeyInterface()
        # Don't exist in keyinterface!
        with self.assertRaises(NotImplementedError):
            keys.getPublicKeys()
        with self.assertRaises(NotImplementedError):
            keys.getPrivateKeyForPublicKey("x")
        with self.assertRaises(NotImplementedError):
            keys.add("x")
        with self.assertRaises(NotImplementedError):
            keys.delete("x")

        x = EncryptedKeyInterface()
        self.assertFalse(x.locked())
        self.assertTrue(x.is_encrypted())

    def test_default_config(self):
        config = storage.get_default_config_store(appname="testing-")
        config["node"]

    def test_default_key(self):
        config = storage.get_default_config_store(appname="testing-")
        keys = storage.get_default_key_store(appname="testing2", config=config)
        keys["node"]

    def test_configstorage(self):
        for config in [
            storage.InRamConfigurationStore(),
            storage.SqliteConfigurationStore(profile="testing"),
        ]:
            config["node"] = "example"
            config["foobar"] = "action"
            self.assertIn("foobar", config)
            self.assertEqual(config["foobar"], "action")

            self.assertTrue(len(list(iter(config))) >= 1)
            self.assertTrue(len(list(config.items())) >= 1)

            self.assertEqual(config.get("non-exist", "bana"), "bana")

            config.delete("foobar")
            config["empty"] = "notempty"
            self.assertNotIn("foobar", config)

            for k in config:
                self.assertIsInstance(k, str)

            for k, v in config.items():
                self.assertIsInstance(k, str)
                self.assertIsInstance(v, str)

            # change a value
            config["change"] = "first"
            self.assertEqual(config["change"], "first")
            config["change"] = "second"
            self.assertEqual(config["change"], "second")

            config.wipe()
            self.assertNotIn("empty", config)

    def test_inramkeystore(self):
        self.do_keystore(storage.InRamPlainKeyStore())

    def test_inramencryptedkeystore(self):
        self.do_keystore(
            storage.InRamEncryptedKeyStore(config=storage.InRamConfigurationStore())
        )

    def test_sqlitekeystore(self):
        s = storage.SqlitePlainKeyStore(profile="testing")
        s.wipe()
        self.do_keystore(s)
        self.assertFalse(s.is_encrypted())

    def test_sqliteencryptedkeystore(self):
        self.do_keystore(
            storage.SqliteEncryptedKeyStore(
                profile="testing", config=storage.InRamConfigurationStore()
            )
        )

    def do_keystore(self, keys):
        keys.wipe()
        password = "foobar"

        if isinstance(
            keys, (storage.SqliteEncryptedKeyStore, storage.InRamEncryptedKeyStore)
        ):
            keys.config.wipe()
            with self.assertRaises(WalletLocked):
                keys.decrypt(
                    "6PRViepa2zaXXGEQTYUsoLM1KudLmNBB1t812jtdKx1TEhQtvxvmtEm6Yh"
                )
            with self.assertRaises(WalletLocked):
                keys.encrypt(
                    "6PRViepa2zaXXGEQTYUsoLM1KudLmNBB1t812jtdKx1TEhQtvxvmtEm6Yh"
                )
            with self.assertRaises(WalletLocked):
                keys._get_encrypted_masterpassword()

            # set the first MasterPassword here!
            keys._new_masterpassword(password)
            keys.lock()
            keys.unlock(password)
            assert keys.unlocked()
            assert keys.is_encrypted()

            with self.assertRaises(bip38.SaltException):
                keys.decrypt(
                    "6PRViepa2zaXXGEQTYUsoLM1KudLmNBB1t812jtdKx1TEhQtvxvmtEm6Yh"
                )

        keys.add(*pubprivpair("5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"))
        # Duplicate key
        with self.assertRaises(KeyAlreadyInStoreException):
            keys.add(
                *pubprivpair("5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3")
            )
        self.assertIn(
            "GPH6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV",
            keys.getPublicKeys(),
        )

        self.assertEqual(
            keys.getPrivateKeyForPublicKey(
                "GPH6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV"
            ),
            "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3",
        )
        self.assertEqual(keys.getPrivateKeyForPublicKey("GPH6MRy"), None)
        self.assertEqual(len(keys.getPublicKeys()), 1)
        keys.add(*pubprivpair("5Hqr1Rx6v3MLAvaYCxLYqaSEsm4eHaDFkLksPF2e1sDS7omneaZ"))
        self.assertEqual(len(keys.getPublicKeys()), 2)
        self.assertEqual(
            keys.getPrivateKeyForPublicKey(
                "GPH5u9tEsKaqtCpKibrXJAMhaRUVBspB5pr9X34PPdrSbvBb6ajZY"
            ),
            "5Hqr1Rx6v3MLAvaYCxLYqaSEsm4eHaDFkLksPF2e1sDS7omneaZ",
        )
        keys.delete("GPH5u9tEsKaqtCpKibrXJAMhaRUVBspB5pr9X34PPdrSbvBb6ajZY")
        self.assertEqual(len(keys.getPublicKeys()), 1)

        if isinstance(
            keys, (storage.SqliteEncryptedKeyStore, storage.InRamEncryptedKeyStore)
        ):
            keys.lock()
            keys.wipe()
            keys.config.wipe()

    def test_masterpassword(self):
        password = "foobar"
        config = storage.InRamConfigurationStore()
        keys = storage.InRamEncryptedKeyStore(config=config)
        self.assertFalse(keys.has_masterpassword())
        master = keys._new_masterpassword(password)
        self.assertEqual(
            len(master),
            len("66eaab244153031e8172e6ffed321" "7288515ddb63646bbefa981a654bdf25b9f"),
        )
        with self.assertRaises(Exception):
            keys._new_masterpassword(master)

        keys.lock()

        with self.assertRaises(Exception):
            keys.change_password("foobar")

        keys.unlock(password)
        self.assertEqual(keys.decrypted_master, master)

        new_pass = "new_secret_password"
        keys.change_password(new_pass)
        keys.lock()
        keys.unlock(new_pass)
        self.assertEqual(keys.decrypted_master, master)

    def test_wrongmastermass(self):
        config = storage.InRamConfigurationStore()
        keys = storage.InRamEncryptedKeyStore(config=config)
        keys._new_masterpassword("foobar")
        keys.lock()
        with self.assertRaises(WrongMasterPasswordException):
            keys.unlock("foobar2")

    def test_masterpwd(self):
        with self.assertRaises(Exception):
            storage.InRamEncryptedKeyStore()
        config = storage.InRamConfigurationStore()
        keys = storage.InRamEncryptedKeyStore(config=config)
        self.assertTrue(keys.locked())
        keys.unlock("foobar")
        keys.password = "FOoo"
        with self.assertRaises(Exception):
            keys._decrypt_masterpassword()
        keys.lock()

        with self.assertRaises(WrongMasterPasswordException):
            keys.unlock("foobar2")

        with self.assertRaises(Exception):
            keys._get_encrypted_masterpassword()

        self.assertFalse(keys.unlocked())

        os.environ["UNLOCK"] = "foobar"
        self.assertTrue(keys.unlocked())

        self.assertFalse(keys.locked())

    def test_inherit_properly(self):
        class MyStore(SQLiteStore):
            pass

        with self.assertRaises(ValueError):
            MyStore()
