from graphenebase.transactions import formatTimeFromNow
from grapheneapi import GrapheneClient
from grapheneextra.proposal import Proposal
from pprint import pprint


symbol = "MILLLIONTDD"
issuer = "jonnybitcoin"
pm_result = False
expiration = formatTimeFromNow(60 * 60 * 24)
proposer = "xeroc"


class Config():
    wallet_host           = "localhost"
    wallet_port           = 8092

if __name__ == '__main__':
    graphene = Proposal(Config)
    account = graphene.rpc.get_account(issuer)
    asset = graphene.rpc.get_asset(symbol)
    # Publish a price
    settle_price = {"quote": {"asset_id": "1.3.0",
                              "amount": 1 if pm_result else 0},
                    "base": {"asset_id": asset["id"],
                             "amount": 1
                             }}
    tx = graphene.rpc.global_settle_asset(symbol, settle_price, False)
    tx = graphene.propose_operations(tx["operations"], expiration, proposer, broadcast=True)
    pprint(tx)
