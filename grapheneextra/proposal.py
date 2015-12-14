from grapheneapi import GrapheneAPI, GrapheneWebsocket
from datetime import datetime
import time

class ProposalManagement(object) :
    wallet  = None
    witness = None

    def __init__(self,config) :
        self.wallet           = GrapheneAPI(config.wallet_host, config.wallet_port, config.wallet_user, config.wallet_password)
        self.witness          = GrapheneWebsocket(config.witness_url, config.witness_user, config.witness_password)

    def approve_available_proposals(self,from_account,approving_account) :
        fromAccount        = self.wallet.get_account(from_account)
        approving_account  = self.wallet.get_account(approving_account)
        proposals          = self.witness.get_proposed_transactions(fromAccount["id"])
        for proposal in proposals : 
            if approving_account["id"] in proposal["available_active_approvals"] :
                print("%s: Proposal %s already approved. Expires on %s UTC" %(fromAccount["name"],proposal['id'], proposal["expiration_time"]))
            else :
                print("%s: Approving Proposal %s ..." %(fromAccount["name"],proposal['id']))
                self.wallet.approve_proposal(approving_account["name"], proposal["id"],{"active_approvals_to_add":[approving_account["name"]]}, True)

    def propose_transfer(self, proposer_account, from_account, to_account, amount, asset, expiration=36000,broadcast=True):
        proposer         = self.wallet.get_account(proposer_account)
        fromAccount      = self.wallet.get_account(from_account)
        toAccount        = self.wallet.get_account(to_account)
        asset            = self.wallet.get_asset(asset)
        op               = self.wallet.get_prototype_operation("transfer_operation")

        op[1]["amount"]["amount"] = int(amount * 10**asset["precision"])
        op[1]["amount"]["asset_id"] = asset["id"]
        op[1]["from"] = fromAccount["id"]
        op[1]["to"]   = toAccount["id"]

        exp_time  = datetime.utcfromtimestamp(time.time()+int(expiration)).strftime('%Y-%m-%dT%H:%M:%S')
        buildHandle = self.wallet.begin_builder_transaction()
        self.wallet.add_operation_to_builder_transaction(buildHandle, op)
        self.wallet.set_fees_on_builder_transaction(buildHandle,asset["id"])
        self.wallet.propose_builder_transaction2(buildHandle, proposer["name"], exp_time, 0, False) 
        self.wallet.set_fees_on_builder_transaction(buildHandle, asset["id"])
        return self.wallet.sign_builder_transaction(buildHandle, broadcast)
