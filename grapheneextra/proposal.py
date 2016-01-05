from datetime import datetime
import time


class Proposal(object) :
    """ Manage Proposals

        :param grapheneapi.GrapheneClient grapheneClient: Grapehen
                    Client instance with connection details for RPC
                    *and* websocket connection

    """
    def __init__(self, grapheneClient) :
        self.client           = grapheneClient

    def approve_available_proposals(self, from_account, approving_account) :
        """ Approve all proposals for a given account with given approver

            :param str from_account: account name to approve *all* proposals for
            :param str approving_account: approving account

        """
        fromAccount        = self.client.rpc.get_account(from_account)
        approving_account  = self.client.rpc.get_account(approving_account)
        proposals          = self.client.ws.get_proposed_transactions(fromAccount["id"])
        for proposal in proposals :
            if approving_account["id"] in proposal["available_active_approvals"] :
                print("%s: Proposal %s already approved. Expires on %s UTC"  %
                      (fromAccount["name"], proposal['id'], proposal["expiration_time"]))
            else :
                print("%s: Approving Proposal %s ..." %
                      (fromAccount["name"], proposal['id']))
                self.client.rpc.approve_proposal(approving_account["name"],
                                                 proposal["id"],
                                                 {"active_approvals_to_add" : [approving_account["name"]]},
                                                 True)

    def propose_transfer(self, proposer_account, from_account, to_account,
                         amount, asset, expiration=3600, broadcast=True):
        """ Propose a Transfer Transaction (opid=0)

            :param str proposer_account: Account that proposed the transfer (and pays the proposal fee)
            :param str from_account: Account to transfer from (pays tx fee)
            :param str to_account: Account to transfer to
            :param init amount: Amount to transfer (*not* in satoshi, e.g. 100.112 BTS)
            :param str asset: Symbol or id of the asset to transfer
            :param expiration: Expiration of the proposal (default: 60min)
            :param bool broadcast: Broadcast signed transaction or not

            .. note:: This method requires
                        ``propose_builder_transaction2`` to be available in the
                        cli_wallet

        """
        proposer         = self.client.rpc.get_account(proposer_account)
        fromAccount      = self.client.rpc.get_account(from_account)
        toAccount        = self.client.rpc.get_account(to_account)
        asset            = self.client.rpc.get_asset(asset)
        op               = self.client.rpc.get_prototype_operation("transfer_operation")

        op[1]["amount"]["amount"]   = int(amount * 10 ** asset["precision"])
        op[1]["amount"]["asset_id"] = asset["id"]
        op[1]["from"]               = fromAccount["id"]
        op[1]["to"]                 = toAccount["id"]

        exp_time    = datetime.utcfromtimestamp(time.time() + int(expiration)).strftime('%Y-%m-%dT%H:%M:%S')
        buildHandle = self.client.rpc.begin_builder_transaction()
        self.client.rpc.add_operation_to_builder_transaction(buildHandle, op)
        self.client.rpc.set_fees_on_builder_transaction(buildHandle, asset["id"])
        self.client.rpc.propose_builder_transaction2(buildHandle, proposer["name"], exp_time, 0, False)
        self.client.rpc.set_fees_on_builder_transaction(buildHandle, asset["id"])
        return self.client.rpc.sign_builder_transaction(buildHandle, broadcast)
