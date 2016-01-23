from grapheneapi import GrapheneWebsocket, GrapheneWebsocketProtocol
from graphenebase import Memo, PrivateKey, PublicKey
import config

#: PubKey Prefix
#:  *  Productive network: BTS
#:  *  Testnetwork: GPH """
# prefix = "GPH"
prefix = "BTS"


class GrapheneMonitor(GrapheneWebsocketProtocol) :
    last_op      = "1.11.0"
    account_id   = "1"

    def __init__(self) :
        super().__init__()

    def onAccountUpdate(self, data=None) :
        if data :
            opID = api.getObject(data["most_recent_op"])["operation_id"]
        else :
            opID = self.last_op
        self.wsexec([self.api_ids["history"], "get_account_history", [self.account_id, self.last_op, 100, "1.11.0"]], self.process_operations)
        if data :
            self.last_op = opID

    def process_operations(self, operations) :
        for operation in operations[::-1] :
            opID         = operation["id"]
            block        = operation["block_num"]
            op           = operation["op"][1]

            " Consider only Transfer operations "
            if operation["op"][0] != 0:
                continue

            # Get assets involved in Fee and Transfer
            fee_asset    = api.getObject(op["fee"]["asset_id"])
            amount_asset = api.getObject(op["amount"]["asset_id"])

            # Amounts for fee and transfer
            fee_amount = float(op["fee"]["amount"]) / float(10 ** int(fee_asset["precision"]))
            amount_amount = float(op["amount"]["amount"]) / float(10 ** int(amount_asset["precision"]))

            # Get accounts involved
            from_account = api.getObject(op["from"])
            to_account   = api.getObject(op["to"])

            # Decode the memo
            memomsg = ""
            if "memo" in op :
                memo         = op["memo"]
                try :  # if possible
                    privkey = PrivateKey(config.memo_wif_key)
                    pubkey  = PublicKey(memo["from"], prefix=prefix)
                    memomsg = Memo.decode_memo(privkey, pubkey, memo["nonce"], memo["message"])
                except Exception as e:  # if not possible
                    memomsg = "--cannot decode-- %s" % str(e)
            # Print out
            print("last_op: %s | block:%s | from %s -> to: %s | fee: %f %s | amount: %f %s | memo: %s" % (
                  opID, block,
                  from_account["name"], to_account["name"],
                  fee_amount, fee_asset["symbol"],
                  amount_amount, amount_asset["symbol"],
                  memomsg))

if __name__ == '__main__':
    # Monitor definitions
    protocol = GrapheneMonitor
    protocol.last_op = config.last_op  # last operation logged
    protocol.account_id = "1.2.%s" % config.accountID.split(".")[2]  # account to monitor

    # Open Up Graphene Websocket API
    api      = GrapheneWebsocket(config.url, config.user, config.password, protocol)

    # Set Callback for object changes
    api.setObjectCallbacks({config.accountID : protocol.onAccountUpdate})
    api.setEventCallbacks({"registered-history" : protocol.onAccountUpdate})

    # Run the Websocket connection continuously
    api.connect()
    api.run_forever()
