from graphenebase import transactions, memo, account
from graphenebase.account import PrivateKey
import random
import unittest
from pprint import pprint
from binascii import hexlify

prefix = "BTS"
wif              = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"
ref_block_num    = 34294
ref_block_prefix = 3707022213
expiration       = "2016-04-06T08:29:27"


class Testcases(unittest.TestCase) :

    def test_call_update(self):
        s = {'fee': {'amount': 100,
                     'asset_id': '1.3.0'},
             'delta_debt': {'amount': 10000,
                            'asset_id': '1.3.22'},
             'delta_collateral': {'amount': 100000000,
                                  'asset_id': '1.3.0'},
             'funding_account': '1.2.29',
             'extensions': []}
        ops = [transactions.Operation(transactions.Call_order_update(**s))]
        tx = transactions.Signed_Transaction(ref_block_num=ref_block_num,
                                             ref_block_prefix=ref_block_prefix,
                                             expiration=expiration,
                                             operations=ops)
        tx     = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")
        compare = "f68585abf4dce7c8045701036400000000000000001d00e1f50500000000001027000000000000160000011f2627efb5c5144440e06ff567f1a09928d699ac6f5122653cd7173362a1ae20205952c874ed14ccec050be1c86c1a300811763ef3b481e562e0933c09b40e31fb"
        self.assertEqual(compare[:-130], txWire[:-130])

    def test_limit_order_create(self):
        s = {"fee": {"amount": 100,
                     "asset_id": "1.3.0"
                     },
             "seller": "1.2.29",
             "amount_to_sell": {"amount": 100000,
                                "asset_id": "1.3.0"
                                },
             "min_to_receive": {"amount": 10000,
                                "asset_id": "1.3.105"
                                },
             "expiration": "2016-05-18T09:22:05",
             "fill_or_kill": False,
             "extensions": []
             }

        ops = [transactions.Operation(transactions.Limit_order_create(**s))]
        tx = transactions.Signed_Transaction(ref_block_num=ref_block_num,
                                             ref_block_prefix=ref_block_prefix,
                                             expiration=expiration,
                                             operations=ops)
        tx     = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")
        compare = "f68585abf4dce7c8045701016400000000000000001da086010000000000001027000000000000693d343c57000000011f75cbfd49ae8d9b04af76cc0a7de8b6e30b71167db7fe8e2197ef9d858df1877043493bc24ffdaaffe592357831c978fd8a296b913979f106debe940d60d77b50"
        self.assertEqual(compare[:-130], txWire[:-130])

    def test_limit_order_cancel(self):
        s = {"fee": {"amount": 0,
                     "asset_id": "1.3.0"
                     },
             "fee_paying_account": "1.2.104",
             "order": "1.7.51840",
             "extensions": []
             }
        ops = [transactions.Operation(transactions.Limit_order_cancel(**s))]
        tx = transactions.Signed_Transaction(ref_block_num=ref_block_num,
                                             ref_block_prefix=ref_block_prefix,
                                             expiration=expiration,
                                             operations=ops)
        tx     = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")
        compare = "f68585abf4dce7c804570102000000000000000000688095030000011f3fb754814f3910c1a8845486b86057d2b4588ae559b4c3810828c0d4cbec0e5b23517937cd7e0cc5ee8999d0777af7fe56d3c4b2e587421bfb7400d4efdae97a"
        self.assertEqual(compare[:-130], txWire[:-130])

    def test_proposal_update(self):
        s = {'fee_paying_account': "1.2.1",
             'proposal': "1.10.90",
             'active_approvals_to_add': ["1.2.5"],
             "fee": transactions.Asset(amount=12512, asset_id="1.3.0"),
             }
        op = transactions.Proposal_update(**s)
        ops    = [transactions.Operation(op)]
        tx     = transactions.Signed_Transaction(ref_block_num=ref_block_num,
                                                 ref_block_prefix=ref_block_prefix,
                                                 expiration=expiration,
                                                 operations=ops)
        tx     = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")
        compare = "f68585abf4dce7c804570117e03000000000000000015a01050000000000000001203255378db6dc19443e74421c954ad7fdcf23f4ea45fe4fe5a1b078a0f94fb529594819c9799d68efa5cfb5b271a9333a2f516ca4fb5093226275f48a42d9e8cf"
        self.assertEqual(compare[:-130], txWire[:-130])

    def test_Transfer(self):
        pub              = format(account.PrivateKey(wif).pubkey, prefix)
        from_account_id  = "1.2.0"
        to_account_id    = "1.2.1"
        amount           = 1000000
        asset_id         = "1.3.4"
        message          = "abcdefgABCDEFG0123456789"
        nonce            = "5862723643998573708"

        fee          = transactions.Asset(amount=0, asset_id="1.3.0")
        amount       = transactions.Asset(amount=int(amount), asset_id=asset_id)
        encrypted_memo = memo.encode_memo(account.PrivateKey(wif),
                                          account.PublicKey(pub, prefix=prefix),
                                          nonce,
                                          message)
        memoStruct = {"from": pub,
                      "to": pub,
                      "nonce": nonce,
                      "message": encrypted_memo,
                      "chain": prefix}
        memoObj  = transactions.Memo(**memoStruct)
        transferStruct = {"fee": fee,
                          "from": from_account_id,
                          "to": to_account_id,
                          "amount": amount,
                          "memo": memoObj
                          }
        transfer = transactions.Transfer(**transferStruct)
        ops    = [transactions.Operation(transfer)]
        tx     = transactions.Signed_Transaction(ref_block_num=ref_block_num,
                                                 ref_block_prefix=ref_block_prefix,
                                                 expiration=expiration,
                                                 operations=ops)
        tx     = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")

        compare = "f68585abf4dce7c804570100000000000000000000000140420f0000000000040102c0ded2bc1f1305fb0faac5e6c03ee3a1924234985427b6167ca569d13df435cf02c0ded2bc1f1305fb0faac5e6c03ee3a1924234985427b6167ca569d13df435cf8c94d19817945c5120fa5b6e83079a878e499e2e52a76a7739e9de40986a8e3bd8a68ce316cee50b210000011f39e3fa7071b795491e3b6851d61e7c959be92cc7deb5d8491cf1c3c8c99a1eb44553c348fb8f5001a78b18233ac66727e32fc776d48e92d9639d64f68e641948"
        self.assertEqual(compare[:-130], txWire[:-130])

    def test_pricefeed(self):
        feed = transactions.PriceFeed(**{
            "settlement_price" : transactions.Price(
                base=transactions.Asset(amount=214211, asset_id="1.3.0"),
                quote=transactions.Asset(amount=1241, asset_id="1.3.14"),
            ),
            "core_exchange_rate" : transactions.Price(
                base=transactions.Asset(amount=1241, asset_id="1.3.0"),
                quote=transactions.Asset(amount=6231, asset_id="1.3.14"),
            ),
            "maximum_short_squeeze_ratio" : 1100,
            "maintenance_collateral_ratio" : 1750,
        })

        pFeed = transactions.Asset_publish_feed(
            fee=transactions.Asset(amount=100, asset_id="1.3.0"),
            publisher="1.2.0",
            asset_id="1.3.3",
            feed=feed
        )

        ops    = [transactions.Operation(pFeed)]
        tx     = transactions.Signed_Transaction(ref_block_num=ref_block_num,
                                                 ref_block_prefix=ref_block_prefix,
                                                 expiration=expiration,
                                                 operations=ops)
        tx     = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")

        compare = "f68585abf4dce7c8045701136400000000000000000003c34403000000000000d9040000000000000ed6064c04d9040000000000000057180000000000000e0000012009e13f9066fedc3c8c1eb2ac33b15dc67ecebf708890d0f8ab62ec8283d1636002315a189f1f5aa8497b41b8e6bb7c4dc66044510fae25d8f6aebb02c7cdef10"
        self.assertEqual(compare[:-130], txWire[:-130])

    def test_jsonLoading(self):
        data1 = {"expiration": expiration,
                 "extensions": [],
                 "operations": [[0,
                                 {"amount": {"amount": 1000000, "asset_id": "1.3.4"},
                                  "extensions": [],
                                  "fee": {"amount": 0, "asset_id": "1.3.0"},
                                  "from": "1.2.0",
                                  "memo": {"from": "BTS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV",
                                           "message": "fa5b6e83079a878e499e2e52a76a7739e9de40986a8e3bd8a68ce316cee50b21",
                                           "nonce": 5862723643998573708,
                                           "to": "BTS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV"},
                                  "to": "1.2.1"}]],
                 "ref_block_num": ref_block_num,
                 "ref_block_prefix": ref_block_prefix,
                 "signatures": ["1f6c1e8df5faf18c3b057ce713ec92f9b487c1ba58138daabc0038741b402c930d63d8d63861740215b4f65eb8ac9185a3987f8239b962181237f47189e21102af"]}
        a = transactions.Signed_Transaction(data1.copy())
        data2 = transactions.JsonObj(a)

        check1 = data1
        check2 = data2
        for key in ["expiration", "extensions", "ref_block_num", "ref_block_prefix", "signatures"]:
            self.assertEqual(check1[key], check2[key])

        check1 = data1["operations"][0][1]
        check2 = data2["operations"][0][1]
        for key in ["from", "to"]:
            self.assertEqual(check1[key], check2[key])

        check1 = data1["operations"][0][1]["memo"]
        check2 = data2["operations"][0][1]["memo"]
        for key in check1:
            self.assertEqual(check1[key], check2[key])

    def test_fee_pool(self):
        s = {"fee": {"amount": 10001,
                     "asset_id": "1.3.0"
                     },
             "from_account": "1.2.282",
             "asset_id": "1.3.32",
             "amount": 15557238,
             "extensions": []
             }
        op = transactions.Asset_fund_fee_pool(**s)
        ops    = [transactions.Operation(op)]
        tx     = transactions.Signed_Transaction(ref_block_num=ref_block_num,
                                                 ref_block_prefix=ref_block_prefix,
                                                 expiration=expiration,
                                                 operations=ops)
        tx     = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")
        compare = "f68585abf4dce7c8045701101127000000000000009a02207662ed00000000000000011f39f7dc7745076c9c7e612d40c68ee92d3f4b2696b1838037ce2a35ac259883ba6c6c49d91ad05a7e78d80bb83482c273dbbc911587487bf468b85fb4f537da3d"
        self.assertEqual(compare[:-130], txWire[:-130])

    def test_override_transfer(self):
        s = {"fee": {"amount": 0,
                     "asset_id": "1.3.0"},
             "issuer": "1.2.29",
             "from": "1.2.104",
             "to": "1.2.29",
             "amount": {"amount": 100000,
                        "asset_id": "1.3.105"},
             "extensions": []
             }
        op = transactions.Override_transfer(**s)
        ops    = [transactions.Operation(op)]
        tx     = transactions.Signed_Transaction(ref_block_num=ref_block_num,
                                                 ref_block_prefix=ref_block_prefix,
                                                 expiration=expiration,
                                                 operations=ops)
        tx     = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")
        compare = "f68585abf4dce7c8045701260000000000000000001d681da08601000000000069000000012030cc81722c3e67442d2f59deba188f6079c8ba2d8318a642e6a70a125655515f20e2bd3adb2ea886cdbc7f6590c7f8c80818d9176d9085c176c736686ab6c9fd"
        self.assertEqual(compare[:-130], txWire[:-130])

    def test_create_account(self):
        s = {"fee": {"amount": 1467634,
                     "asset_id": "1.3.0"
                     },
             "registrar": "1.2.33",
             "referrer": "1.2.27",
             "referrer_percent": 3,
             "name": "foobar-f124",
             "owner": {"weight_threshold": 1,
                       "account_auths": [],
                       'key_auths': [['BTS6pbVDAjRFiw6fkiKYCrkz7PFeL7XNAfefrsREwg8MKpJ9VYV9x',
                                     1], [
                                     'BTS6zLNtyFVToBsBZDsgMhgjpwysYVbsQD6YhP3kRkQhANUB4w7Qp',
                                     1]],
                       "address_auths": []
                       },
             "active": {"weight_threshold": 1,
                        "account_auths": [],
                        'key_auths': [['BTS6pbVDAjRFiw6fkiKYCrkz7PFeL7XNAfefrsREwg8MKpJ9VYV9x',
                                       1], [
                                      'BTS6zLNtyFVToBsBZDsgMhgjpwysYVbsQD6YhP3kRkQhANUB4w7Qp',
                                      1], [
                                      'BTS8CemMDjdUWSV5wKotEimhK6c4dY7p2PdzC2qM1HpAP8aLtZfE7',
                                      1
                                      ]],
                        "address_auths": []
                        },
             "options": {"memo_key": "BTS5TPTziKkLexhVKsQKtSpo4bAv5RnB8oXcG4sMHEwCcTf3r7dqE",
                         "voting_account": "1.2.5",
                         "num_witness": 0,
                         "num_committee": 0,
                         "votes": [],
                         "extensions": []
                         },
             "extensions": {}
             }
        op = transactions.Account_create(**s)
        ops    = [transactions.Operation(op)]
        tx     = transactions.Signed_Transaction(ref_block_num=ref_block_num,
                                                 ref_block_prefix=ref_block_prefix,
                                                 expiration=expiration,
                                                 operations=ops)
        tx     = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")
        compare = "f68585abf4dce7c804570105f26416000000000000211b03000b666f6f6261722d6631323401000000000202fe8cc11cc8251de6977636b55c1ab8a9d12b0b26154ac78e56e7c4257d8bcf6901000314aa202c9158990b3ec51a1aa49b2ab5d300c97b391df3beb34bb74f3c62699e01000001000000000303b453f46013fdbccb90b09ba169c388c34d84454a3b9fbec68d5a7819a734fca0010002fe8cc11cc8251de6977636b55c1ab8a9d12b0b26154ac78e56e7c4257d8bcf6901000314aa202c9158990b3ec51a1aa49b2ab5d300c97b391df3beb34bb74f3c62699e010000024ab336b4b14ba6d881675d1c782912783c43dbbe31693aa710ac1896bd7c3d61050000000000000000011f61ad276120bc3f1892962bfff7db5e8ce04d5adec9309c80529e3a978a4fa1073225a6d56929e34c9d2a563e67a8f4a227e4fadb4a3bb6ec91bfdf4e57b80efd"
        self.assertEqual(compare[:-130], txWire[:-130])

    def test_create_proposal(self):
        s = {"fee": {"amount": 0,
                     "asset_id": "1.3.0"
                     },
             "fee_paying_account": "1.2.0",
             "expiration_time": "1970-01-01T00:00:00",
             "proposed_ops": [{
                 "op": [
                     0, {"fee": {"amount": 0,
                                 "asset_id": "1.3.0"
                                 },
                         "from": "1.2.0",
                         "to": "1.2.0",
                         "amount": {"amount": 0,
                                    "asset_id": "1.3.0"
                                    },
                         "extensions": []}]}],
             "extensions": []}
        op = transactions.Proposal_create(**s)
        ops    = [transactions.Operation(op)]
        tx     = transactions.Signed_Transaction(ref_block_num=ref_block_num,
                                                 ref_block_prefix=ref_block_prefix,
                                                 expiration=expiration,
                                                 operations=ops)
        tx     = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")
        compare = ("f68585abf4dce7c80457011600000000000000000000000000"
                   "00010000000000000000000000000000000000000000000000"
                   "00000001204baf7f11a7ff12337fc097ac6e82e7b68f82f02c"
                   "c7e24231637c88a91ae5716674acec8a1a305073165c65e520"
                   "a64769f5f62c0301ce21ab4f7c67a6801b4266")
        self.assertEqual(compare[:-130], txWire[:-130])

    def test_asset_update(self):
        op = transactions.Asset_update(**{
            "fee": {"amount": 0,
                    "asset_id": "1.3.0"},
            "issuer": "1.2.0",
            "asset_to_update": "1.3.0",
            "new_options": {
                "max_supply": "1000000000000000",
                "market_fee_percent": 0,
                "max_market_fee": "1000000000000000",
                "issuer_permissions": 79,
                "flags": 0,
                "core_exchange_rate": {
                    "base": {"amount": 0,
                             "asset_id": "1.3.0"},
                    "quote": {"amount": 0,
                              "asset_id": "1.3.0"}
                },
                "whitelist_authorities": ["1.2.12", "1.2.13"],
                "blacklist_authorities": ["1.2.10", "1.2.11"],
                "whitelist_markets": ["1.3.10", "1.3.11"],
                "blacklist_markets": ["1.3.12", "1.3.13"],
                "description": "Foobar",
                "extensions": []
            },
            "extensions": []
        })
        ops    = [transactions.Operation(op)]
        tx     = transactions.Signed_Transaction(ref_block_num=ref_block_num,
                                                 ref_block_prefix=ref_block_prefix,
                                                 expiration=expiration,
                                                 operations=ops)
        tx     = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")
        compare = ("f68585abf4dce7c80457010b00000000000000000000000000"
                   "80c6a47e8d030000000080c6a47e8d03004f00000000000000"
                   "0000000000000000000000000000020c0d020a0b020a0b020c"
                   "0d06466f6f626172000000011f5bd6a206d210d1d78eb423e0"
                   "c2362013aa80830a8e61e5df2570eac05f1c57a4165c99099f"
                   "c2e97ecbf2b46014c96a6f99cff8d20f55a6042929136055e5"
                   "ad10")
        self.assertEqual(compare[:-130], txWire[:-130])

    def test_whitelist(self):
        op = transactions.Account_whitelist(**{
            "fee": {"amount": 0,
                    "asset_id": "1.3.0"},
            "authorizing_account": "1.2.0",
            "account_to_list": "1.2.1",
            "new_listing": 0x1,
            "extensions": []
        })
        ops    = [transactions.Operation(op)]
        tx     = transactions.Signed_Transaction(ref_block_num=ref_block_num,
                                                 ref_block_prefix=ref_block_prefix,
                                                 expiration=expiration,
                                                 operations=ops)
        tx     = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")
        compare = ("f68585abf4dce7c8045701070000000000000000000001010"
                   "000011f14eef2978e40b369273907072dddf4b4043d9f3a08"
                   "da125311c4e6b54b3e7c2a3606594fab7cf6ce381544eceda"
                   "9945c8c9fccebd587cfa2d2f6a146b1639f8c")
        self.assertEqual(compare[:-130], txWire[:-130])

    def compareConstructedTX(self):
        #    def test_online(self):
        #        self.maxDiff = None
        op = transactions.Account_whitelist(**{
            "fee": {"amount": 0,
                    "asset_id": "1.3.0"},
            "authorizing_account": "1.2.0",
            "account_to_list": "1.2.1",
            "new_listing": 0x1,
            "extensions": []
        })
        ops = [transactions.Operation(op)]
        tx = transactions.Signed_Transaction(
            ref_block_num=ref_block_num,
            ref_block_prefix=ref_block_prefix,
            expiration=expiration,
            operations=ops
        )
        tx     = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")
        print("=" * 80)
        pprint(tx.json())
        print("=" * 80)

        from grapheneapi.grapheneapi import GrapheneAPI
        rpc = GrapheneAPI("localhost", 8092)
        compare = rpc.serialize_transaction(tx.json())
        print(compare[:-130])
        print(txWire[:-130])
        print(txWire[:-130] == compare[:-130])
        self.assertEqual(compare[:-130], txWire[:-130])

    def compareNewWire(self):
        #    def test_online(self):
        #        self.maxDiff = None

        from grapheneapi.grapheneapi import GrapheneAPI
        rpc = GrapheneAPI("localhost", 8092)
        tx = rpc.create_account("xeroc", "fsafaasf", "", False)
        pprint(tx)
        compare = rpc.serialize_transaction(tx)
        ref_block_num    = tx["ref_block_num"]
        ref_block_prefix = tx["ref_block_prefix"]
        expiration       = tx["expiration"]

        ops    = [transactions.Operation(transactions.Account_create(**tx["operations"][0][1]))]
        tx     = transactions.Signed_Transaction(ref_block_num=ref_block_num,
                                                 ref_block_prefix=ref_block_prefix,
                                                 expiration=expiration,
                                                 operations=ops)
        tx     = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")
        print("\n")
        print(txWire[:-130])
        print(compare[:-130])
        # self.assertEqual(compare[:-130], txWire[:-130])

if __name__ == '__main__':
    t = Testcases()
    t.compareConstructedTX()
