from grapheneapi.grapheneclient import GrapheneClient
from graphenebase.transactions import getOperationNameForId
from pprint import pprint
from deepdiff import DeepDiff

proposer = "xeroc"
expiration = "2016-05-17T09:00:00"
price_per_kbyte = 0
everythin_flat_fee = 0.001
broadcast = True


class Wallet():
    wallet_host = "localhost"
    wallet_port = 8092

if __name__ == '__main__':
    graphene = GrapheneClient(Wallet)
    obj = graphene.getObject("2.0.0")
    current_fees = obj["parameters"]["current_fees"]["parameters"]
    old_fees = obj["parameters"]["current_fees"]
    scale = obj["parameters"]["current_fees"]["scale"] / 1e4

    # General change of parameter
    changes = {}
    for f in current_fees:
        if ("price_per_kbyte" in f[1] and f[1]["price_per_kbyte"] != 0):
            print("Changing operation %s[%d]" % (getOperationNameForId(
                f[0]), f[0]))
            changes[getOperationNameForId(f[0])] = f[1].copy()
            changes[getOperationNameForId(f[0])]["price_per_kbyte"] = int(
                price_per_kbyte / scale * 1e5)
        if ("fee" in f[1] and f[1]["fee"] != 0):
            print("Changing operation %s[%d]" % (getOperationNameForId(
                f[0]), f[0]))
            changes[getOperationNameForId(f[0])] = f[1].copy()
            changes[getOperationNameForId(f[0])]["fee"] = int(
                everythin_flat_fee / scale * 1e5)

    # overwrite / set specific fees
    changes["transfer"]["price_per_kbyte"]       = int(0)
    # changes["account_update"]["price_per_kbyte"] = int(   5 / scale * 1e5)

    print("=" * 80)
    tx = graphene.rpc.propose_fee_change(proposer,
                                         expiration,
                                         changes,
                                         broadcast)
    proposed_ops = tx["operations"][0][1]["proposed_ops"][0]
    new_fees = proposed_ops["op"][1]["new_parameters"]["current_fees"]

    pprint(DeepDiff(old_fees, new_fees))

    if not broadcast:
        print("=" * 80)
        print("Set broadcast to 'True' if the transaction shall be broadcast!")
