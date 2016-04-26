from graphenebase import transactions, memo, account
import random
import unittest
from pprint import pprint
from binascii import hexlify


class Testcases(unittest.TestCase) :

    def test_Transfer(self):
        prefix           = "BTS"
        wif              = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"
        pub              = format(account.PrivateKey(wif).pubkey, prefix)
        from_account_id  = "1.2.0"
        to_account_id    = "1.2.1"
        amount           = 1000000
        asset_id         = "1.3.4"
        message          = "abcdefgABCDEFG0123456789"
        nonce            = "5862723643998573708"
        ref_block_num    = 34294
        ref_block_prefix = 3707022213
        expiration       = "2016-04-06T08:29:27"

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

        prefix           = "BTS"
        wif              = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"
        ref_block_num    = 34294
        ref_block_prefix = 3707022213
        expiration       = "2016-04-06T08:29:27"

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

        data1 = {"expiration": "2016-04-06T08:29:27",
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
                 "ref_block_num": 34294,
                 "ref_block_prefix": 3707022213,
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
