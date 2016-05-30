from graphenebase import transactions, memo, account
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
        txWire = hexlify(bytes(tx)).decode("ascii")
        compare = "f68585abf4dce7c8045701101127000000000000009a02207662ed00000000000000011f39f7dc7745076c9c7e612d40c68ee92d3f4b2696b1838037ce2a35ac259883ba6c6c49d91ad05a7e78d80bb83482c273dbbc911587487bf468b85fb4f537da3d"
        self.assertEqual(compare[:-130], txWire[:-130])

    def compareConstructedTX(self):
        #    def test_online(self):
        #        self.maxDiff = None
        op = transactions.Asset_fund_fee_pool(
            **{"fee": {"amount": 10001,
                       "asset_id": "1.3.0"
                       },
               "from_account": "1.2.282",
               "asset_id": "1.3.32",
               "amount": 15557238,
               "extensions": []
               }
        )

        ops = [transactions.Operation(op)]
        tx = transactions.Signed_Transaction(
            ref_block_num=ref_block_num,
            ref_block_prefix=ref_block_prefix,
            expiration=expiration,
            operations=ops
        )
        tx     = tx.sign([wif], chain=prefix)
        txWire = hexlify(bytes(tx)).decode("ascii")

        from grapheneapi.grapheneapi import GrapheneAPI
        rpc = GrapheneAPI("localhost", 8092)
        compare = rpc.serialize_transaction(transactions.JsonObj(tx))
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
        txWire = hexlify(bytes(tx)).decode("ascii")
        print("\n")
        print(txWire[:-130])
        print(compare[:-130])
        # self.assertEqual(compare[:-130], txWire[:-130])

if __name__ == '__main__':
    t = Testcases()
    t.compareConstructedTX()
