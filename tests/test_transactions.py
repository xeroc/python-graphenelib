# -*- coding: utf-8 -*-
import unittest

from pprint import pprint
from binascii import hexlify
from datetime import datetime, timedelta, timezone

from .fixtures import (
    formatTimeFromNow,
    timeformat,
    Account_create,
    Operation,
    Signed_Transaction,
    MissingSignatureForKey,
    PrivateKey,
    PublicKey,
)


prefix = "GPH"
wif = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"
ref_block_num = 34294
ref_block_prefix = 3707022213
expiration = "2016-04-06T08:29:27"


class Testcases(unittest.TestCase):
    def doit(self, printWire=False):
        tx = Signed_Transaction(
            ref_block_num=ref_block_num,
            ref_block_prefix=ref_block_prefix,
            expiration=expiration,
            operations=[self.op],
        )
        self.assertEqual(tx.id, "0e67819255826ebe19c81f850cb8bf880a5ea9be")

        # No let's wrap ops in Operation!
        tx = Signed_Transaction(
            ref_block_num=ref_block_num,
            ref_block_prefix=ref_block_prefix,
            expiration=expiration,
            operations=[Operation(self.op)],
        )
        self.assertEqual(tx.id, "0e67819255826ebe19c81f850cb8bf880a5ea9be")

        # Sign with prefix
        tx = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], prefix)
        txWire = hexlify(bytes(tx)).decode("ascii")

        # Sign with manual chain id object
        tx2 = tx.sign(
            [wif],
            chain={
                "chain_id": "b8d1603965b3eb1acba27e62ff59f74efa3154d43a4188d381088ac7cdf35539",
                "core_symbol": "CORE",
                "prefix": "GPH",
            },
        )
        tx2.verify([PrivateKey(wif).pubkey], "GPH")
        txWire2 = hexlify(bytes(tx)).decode("ascii")

        # identify by chain id
        tx3 = tx.sign(
            [wif],
            chain="b8d1603965b3eb1acba27e62ff59f74efa3154d43a4188d381088ac7cdf35539",
        )
        tx3.verify([PrivateKey(wif).pubkey], "GPH")
        txWire3 = hexlify(bytes(tx)).decode("ascii")

        if printWire:
            print()
            print(txWire)
            print()

        # Compare expected result with test unit
        self.assertEqual(self.cm[:-130], txWire[:-130])
        self.assertEqual(self.cm[:-130], txWire2[:-130])
        self.assertEqual(self.cm[:-130], txWire3[:-130])

    def test_signed_transaction(self):
        self.op = Account_create(
            **{
                "fee": {"amount": 1467634, "asset_id": "1.3.0"},
                "registrar": "1.2.33",
                "referrer": "1.2.27",
                "referrer_percent": 3,
                "name": "foobar-f124",
                "owner": {
                    "weight_threshold": 1,
                    "account_auths": [],
                    "key_auths": [
                        ["GPH6pbVDAjRFiw6fkiKYCrkz7PFeL7XNAfefrsREwg8MKpJ9VYV9x", 1]
                    ],
                    "address_auths": [],
                },
                "active": {
                    "weight_threshold": 1,
                    "account_auths": [],
                    "key_auths": [
                        ["GPH6pbVDAjRFiw6fkiKYCrkz7PFeL7XNAfefrsREwg8MKpJ9VYV9x", 1]
                    ],
                    "address_auths": [],
                },
                "options": {
                    "memo_key": "GPH5TPTziKkLexhVKsQKtSpo4bAv5RnB8oXcG4sMHEwCcTf3r7dqE",
                    "voting_account": "1.2.5",
                    "num_witness": 0,
                    "num_committee": 0,
                    "votes": [],
                    "extensions": [],
                },
                "extensions": {},
                "prefix": "GPH",
            }
        )
        tx = Signed_Transaction(
            ref_block_num=ref_block_num,
            ref_block_prefix=ref_block_prefix,
            expiration=expiration,
            operations=[self.op],
        )
        self.assertIn("chain_id", tx.getChainParams("GPH"))
        self.assertIn(
            "chain_id",
            tx.getChainParams(
                {
                    "chain_id": "b8d1603965b3eb1acba27e62ff59f74efa3154d43a4188d381088ac7cdf35539",
                    "core_symbol": "CORE",
                    "prefix": "GPH",
                }
            ),
        )
        with self.assertRaises(ValueError):
            self.assertIn(
                "chain_id", tx.getChainParams({"core_symbol": "CORE", "prefix": "GPH"})
            )
        with self.assertRaises(ValueError):
            self.assertIn("chain_id", tx.getChainParams(list()))

        tx.sign([wif])
        # Test for duplicates, does not raise!
        tx.sign([wif, wif])
        tx.verify()
        with self.assertRaises(ValueError):
            tx.verify(["GPH6pbVDAjRFiw6fkiKYCrkz7PFeL7XNAfefrsREwg8MKpJ9VYV9x"])
        with self.assertRaises(MissingSignatureForKey):
            tx.verify(
                [PublicKey("GPH6pbVDAjRFiw6fkiKYCrkz7PFeL7XNAfefrsREwg8MKpJ9VYV9x")]
            )
        tx.verify([PrivateKey(wif).pubkey])

    def test_create_account(self):
        self.op = Account_create(
            **{
                "fee": {"amount": 1467634, "asset_id": "1.3.0"},
                "registrar": "1.2.33",
                "referrer": "1.2.27",
                "referrer_percent": 3,
                "name": "foobar-f124",
                "owner": {
                    "weight_threshold": 1,
                    "account_auths": [],
                    "key_auths": [
                        ["GPH6pbVDAjRFiw6fkiKYCrkz7PFeL7XNAfefrsREwg8MKpJ9VYV9x", 1],
                        ["GPH6zLNtyFVToBsBZDsgMhgjpwysYVbsQD6YhP3kRkQhANUB4w7Qp", 1],
                    ],
                    "address_auths": [],
                },
                "active": {
                    "weight_threshold": 1,
                    "account_auths": [],
                    "key_auths": [
                        ["GPH6pbVDAjRFiw6fkiKYCrkz7PFeL7XNAfefrsREwg8MKpJ9VYV9x", 1],
                        ["GPH6zLNtyFVToBsBZDsgMhgjpwysYVbsQD6YhP3kRkQhANUB4w7Qp", 1],
                        ["GPH8CemMDjdUWSV5wKotEimhK6c4dY7p2PdzC2qM1HpAP8aLtZfE7", 1],
                    ],
                    "address_auths": [],
                },
                "options": {
                    "memo_key": "GPH5TPTziKkLexhVKsQKtSpo4bAv5RnB8oXcG4sMHEwCcTf3r7dqE",
                    "voting_account": "1.2.5",
                    "num_witness": 0,
                    "num_committee": 0,
                    "votes": [],
                    "extensions": [],
                },
                "extensions": {
                    "buyback_options": {
                        "asset_to_buy": "1.3.127",
                        "asset_to_buy_issuer": "1.2.31",
                        "markets": ["1.3.20"],
                    },
                    "null_ext": {},
                    "owner_special_authority": [
                        1,
                        {"asset": "1.3.127", "num_top_holders": 10},
                    ],
                },
                "prefix": "GPH",
            }
        )
        self.cm = (
            "f68585abf4dce7c804570105f26416000000000000211b03000b666f"
            "6f6261722d6631323401000000000202fe8cc11cc8251de6977636b5"
            "5c1ab8a9d12b0b26154ac78e56e7c4257d8bcf6901000314aa202c91"
            "58990b3ec51a1aa49b2ab5d300c97b391df3beb34bb74f3c62699e01"
            "000001000000000303b453f46013fdbccb90b09ba169c388c34d8445"
            "4a3b9fbec68d5a7819a734fca0010002fe8cc11cc8251de6977636b5"
            "5c1ab8a9d12b0b26154ac78e56e7c4257d8bcf6901000314aa202c91"
            "58990b3ec51a1aa49b2ab5d300c97b391df3beb34bb74f3c62699e01"
            "0000024ab336b4b14ba6d881675d1c782912783c43dbbe31693aa710"
            "ac1896bd7c3d610500000000000000000120508168b9615d48bd1184"
            "6b3b9bcf000d1424a7915fb1cfa7f61150b5435c060b3147c056a1f8"
            "89633c43d1b88cb463e8083fa2b62a585af9e1b7a7c23d83ae78"
        )
        self.doit()

    def test_create_account_sort_keys(self):
        self.op = Account_create(
            **{
                "fee": {"amount": 1467634, "asset_id": "1.3.0"},
                "registrar": "1.2.33",
                "referrer": "1.2.27",
                "referrer_percent": 3,
                "name": "foobar-f124",
                "owner": {
                    "weight_threshold": 1,
                    "account_auths": [],
                    "key_auths": [
                        ["GPH6zLNtyFVToBsBZDsgMhgjpwysYVbsQD6YhP3kRkQhANUB4w7Qp", 1],
                        ["GPH6pbVDAjRFiw6fkiKYCrkz7PFeL7XNAfefrsREwg8MKpJ9VYV9x", 1],
                    ],
                    "address_auths": [],
                },
                "active": {
                    "weight_threshold": 1,
                    "account_auths": [],
                    "key_auths": [
                        ["GPH8CemMDjdUWSV5wKotEimhK6c4dY7p2PdzC2qM1HpAP8aLtZfE7", 1],
                        ["GPH6zLNtyFVToBsBZDsgMhgjpwysYVbsQD6YhP3kRkQhANUB4w7Qp", 1],
                        ["GPH6pbVDAjRFiw6fkiKYCrkz7PFeL7XNAfefrsREwg8MKpJ9VYV9x", 1],
                    ],
                    "address_auths": [],
                },
                "options": {
                    "memo_key": "GPH5TPTziKkLexhVKsQKtSpo4bAv5RnB8oXcG4sMHEwCcTf3r7dqE",
                    "voting_account": "1.2.5",
                    "num_witness": 0,
                    "num_committee": 0,
                    "votes": [],
                    "extensions": [],
                },
                "extensions": {
                    "buyback_options": {
                        "asset_to_buy": "1.3.127",
                        "asset_to_buy_issuer": "1.2.31",
                        "markets": ["1.3.20"],
                    },
                    "null_ext": {},
                    "owner_special_authority": [
                        1,
                        {"asset": "1.3.127", "num_top_holders": 10},
                    ],
                },
                "prefix": "GPH",
            }
        )
        self.cm = (
            "f68585abf4dce7c804570105f26416000000000000211b03000b666f"
            "6f6261722d6631323401000000000202fe8cc11cc8251de6977636b5"
            "5c1ab8a9d12b0b26154ac78e56e7c4257d8bcf6901000314aa202c91"
            "58990b3ec51a1aa49b2ab5d300c97b391df3beb34bb74f3c62699e01"
            "000001000000000303b453f46013fdbccb90b09ba169c388c34d8445"
            "4a3b9fbec68d5a7819a734fca0010002fe8cc11cc8251de6977636b5"
            "5c1ab8a9d12b0b26154ac78e56e7c4257d8bcf6901000314aa202c91"
            "58990b3ec51a1aa49b2ab5d300c97b391df3beb34bb74f3c62699e01"
            "0000024ab336b4b14ba6d881675d1c782912783c43dbbe31693aa710"
            "ac1896bd7c3d610500000000000000000120508168b9615d48bd1184"
            "6b3b9bcf000d1424a7915fb1cfa7f61150b5435c060b3147c056a1f8"
            "89633c43d1b88cb463e8083fa2b62a585af9e1b7a7c23d83ae78"
        )
        self.doit()

    def test_timefromnow(self):
        # Careful! This does not do UTC! but takes the local time!
        t = formatTimeFromNow(60)
        t2 = datetime.strptime(t, "%Y-%m-%dT%H:%M:%S")
        self.assertIsInstance(t, str)
        self.assertGreater(t2, datetime.utcnow())
        self.assertGreater(t2, datetime.utcnow() + timedelta(seconds=59))
        self.assertLess(t2, datetime.utcnow() + timedelta(seconds=61))


if __name__ == "__main__":
    t = Testcases()
    t.compareConstructedTX()
