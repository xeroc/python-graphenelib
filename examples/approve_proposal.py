from grapheneapi.grapheneclient import GrapheneClient
from pprint import pprint


class config():
    witness_url = "ws://testnet.bitshares.eu/ws"
    wallet_host = "localhost"
    wallet_port = 8092


if __name__ == '__main__':
    client = GrapheneClient(config)
    graphene = client.rpc

    # Get current fees
    core_asset = graphene.get_asset("1.3.0")
    committee_account = graphene.get_account("committee-account")
    proposals = client.ws.get_proposed_transactions(committee_account["id"])

    for proposal in proposals:
        print("Proposal: %s" % proposal["id"])

        prop_op = proposal["proposed_transaction"]["operations"]

        if len(prop_op) > 1:
            print(" - [Warning] This proposal has more than 1 operation")

        if graphene._confirm("Approve?"):
            tx = graphene.approve_proposal(
                "xeroc",
                proposal["id"],
                {"active_approvals_to_add":
                    ["committee-member-1",
                     "committee-member-2",
                     "committee-member-3",
                     "committee-member-4",
                     "committee-member-5",
                     "committee-member-6",
                     "committee-member-7",
                     "init0",
                     "init1",
                     "init2",
                     "init3",
                     ]},
                True)
            pprint(tx)
