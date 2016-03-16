from grapheneapi.grapheneclient import GrapheneClient
from graphenebase import transactions, memo, account
import random
import unittest
from pprint import pprint
from binascii import hexlify


class Config():
    wallet_host       = "localhost"
    wallet_port       = 8092

    witness_url       = "ws://localhost:8090/"
    wif               = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"
    from_account_name = "nathan"
    to_account_name   = "init0"
    amount            = 10
    asset_name        = "CORE"
    message           = "abcdefgABCDEFG0123456789"
    prefix            = "GPH"


class Testcases(unittest.TestCase) :
    def setUp(self):
        try:
            self.client = GrapheneClient(Config)
            self.connected_chain = self.client.getChainInfo()
            self.skipTests = False
        except:
            print("[Warning] Couldn't connect to witness node or cli-wallet. Skipping tests")
            self.skipTests = True

    def constructWireFormat(self, ops):
        ops        = transactions.addRequiresFees(self.client.ws, ops, "1.3.0")
        ref_block_num, ref_block_prefix = transactions.getBlockParams(self.client.ws)
        expiration = transactions.formatTimeFromNow(30)
        signed     = transactions.Signed_Transaction(ref_block_num, ref_block_prefix, expiration, ops)
        w          = signed.sign([Config.wif], chain=self.connected_chain)
        return w

    def test_Transfer(self):
        if self.skipTests:
            return
        to_account   = self.client.ws.get_account(Config.to_account_name)
        from_account = self.client.ws.get_account(Config.from_account_name)
        asset        = self.client.ws.get_asset(Config.asset_name)
        fee          = transactions.Asset(0, "1.3.0")
        amount       = transactions.Asset(int(Config.amount * 10 ** asset["precision"]), "1.3.0")
        nonce        = str(random.getrandbits(64))
        encrypted_memo = memo.encode_memo(account.PrivateKey(Config.wif),
                                          account.PublicKey(to_account["options"]["memo_key"], prefix=Config.prefix),
                                          nonce,
                                          Config.message)
        memoObj  = transactions.Memo(from_account["options"]["memo_key"],
                                     to_account["options"]["memo_key"],
                                     nonce, encrypted_memo,
                                     chain=self.connected_chain)
        transfer = transactions.Transfer(fee,
                                         from_account["id"],
                                         to_account["id"],
                                         amount,
                                         memoObj)
        ops    = [transactions.Operation(transfer)]
        tx     = self.constructWireFormat(ops)
        txJson = transactions.JsonObj(tx)

        # Let client sign the tx
        clienttxJson = txJson.copy()
        clienttxJson["signatures"] = []
        clienttxJson = self.client.rpc.sign_transaction(clienttxJson, False)
        clienttxWire = self.client.rpc.serialize_transaction(clienttxJson)

        # Fix Expiration and other tx data
        tx.data["expiration"] = transactions.PointInTime(clienttxJson["expiration"])
        tx.data["ref_block_num"] = transactions.Uint16(clienttxJson["ref_block_num"])
        tx.data["ref_block_prefix"] = transactions.Uint32(clienttxJson["ref_block_prefix"])
        txWire = hexlify(bytes(tx)).decode("ascii")

        # Compare
        self.assertEqual(clienttxWire[:-130], txWire[:-130])
