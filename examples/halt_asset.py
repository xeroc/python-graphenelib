from grapheneapi.grapheneclient import GrapheneClient
import json

symbol = "TOKEN"

class Config():
    wallet_host           = "localhost"
    wallet_port           = 8092
    wallet_user           = ""
    wallet_password       = ""

## no edits below this line #####################
perm = {}
perm["charge_market_fee"] = 0x01
perm["white_list"] = 0x02
perm["override_authority"] = 0x04
perm["transfer_restricted"] = 0x08
perm["disable_force_settle"] = 0x10
perm["global_settle"] = 0x20
perm["disable_confidential"] = 0x40
perm["witness_fed_asset"] = 0x80
perm["committee_fed_asset"] = 0x100

graphene = GrapheneClient(Config)
nullaccount = graphene.rpc.get_account("null-account")
asset = graphene.rpc.get_asset(symbol)
flags       = {
               "white_list" : True,
               "transfer_restricted" : True,
               }
flags_int = 0
for p in flags :
    if flags[p]:
        flags_int += perm[p]
options = asset["options"]

options.update({
    "flags" : flags_int,
    "whitelist_authorities" : [nullaccount["id"]],
    "blacklist_authorities" : [nullaccount["id"]],
    "whitelist_markets" : [],
    "blacklist_markets" : [],
})

tx = graphene.rpc.update_asset(symbol, None, options, True)
print(json.dumps(tx, indent=4))
