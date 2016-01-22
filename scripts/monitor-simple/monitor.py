from grapheneapi import GrapheneClient, GrapheneWebsocketProtocol
from graphenebase import Memo, PrivateKey, PublicKey


class Config(GrapheneWebsocketProtocol):
    wallet_host           = "localhost"
    wallet_port           = 8092
    wallet_user           = ""
    wallet_password       = ""
    witness_url           = "ws://testnet.bitshares.eu:11011/"
    witness_user          = ""
    witness_password      = ""

    watch_accounts        = ["faucet"]
    memo_wif_keys         = {
        "faucet": "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"
    }

    last_op               = "1.11.0"

    def __init__(self) :
        super().__init__()

    """
    On Account Update will be registered by GrapheneClient and
    will be called whenever an account or account balance of accounts in
    'watch_accounts' changes (e.g.) on new deposits
    """
    def onAccountUpdate(self, data):
        if "most_recent_op" in data:  # only consider balance updates
            for name in self.watch_accounts:
                opIDObj = graphene.getObject(data["most_recent_op"])
                opID    = opIDObj["operation_id"]
                account = graphene.rpc.get_account(name)
                self.getAccountHistory(account["id"], self.process_operations,
                                       self.last_op, "1.11.0", 100)
                self.last_op = opID

    def process_operations(self, operations) :
        for operation in operations[::-1] :
            opID         = operation["id"]
            block        = operation["block_num"]
            op           = operation["op"][1]

            if operation["op"][0] != 0 :
                continue

            " Get assets involved in Fee and Transfer "
            fee_asset    = graphene.getObject(op["fee"]["asset_id"])
            amount_asset = graphene.getObject(op["amount"]["asset_id"])

            " Amounts for fee and transfer "
            fee_amount    = float(op["fee"]["amount"]) / float(
                10 ** int(fee_asset["precision"]))
            amount_amount = float(op["amount"]["amount"]) / float(
                10 ** int(amount_asset["precision"]))

            " Get accounts involved "
            from_account = graphene.getObject(op["from"])
            to_account   = graphene.getObject(op["to"])

            " Decode the memo "
            memomsg = ""
            if "memo" in op :
                memo         = op["memo"]
                try :
                    account_name = to_account["name"]
                    if account_name not in self.memo_wif_keys:
                        memomsg = "-- missing wif key for %s" % account_name
                    else :
                        privkey = PrivateKey(self.memo_wif_keys[account_name])
                        pubkey  = PublicKey(memo["from"], prefix=self.prefix)
                        memomsg = Memo.decode_memo(privkey, pubkey,
                                                   memo["nonce"],
                                                   memo["message"])
                except Exception as e:
                    memomsg = "--cannot decode-- (%s)" % str(e)

            " Print out "
            print(("last_op: %s | block:%s | from %s -> to: %s " +
                  "| fee: %f %s | amount: %f %s | memo: %s") % (
                      opID, block,
                      from_account["name"], to_account["name"],
                      fee_amount, fee_asset["symbol"],
                      amount_amount, amount_asset["symbol"],
                      memomsg))

            " Store this as last op seen"
            self.last_op = opID

    def onRegisterHistory(self):
        for name in self.watch_accounts:
            account = graphene.rpc.get_account(name)
            self.getAccountHistory(account["id"], self.process_operations,
                                   self.last_op, "1.11.0", 100)

if __name__ == '__main__':
    config = Config
    graphene = GrapheneClient(config)
    graphene.run()
