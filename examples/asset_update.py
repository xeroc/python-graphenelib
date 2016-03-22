from grapheneapi import GrapheneClient
import json

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


class Config():
    wallet_host           = "localhost"
    wallet_port           = 8092
    wallet_user           = ""
    wallet_password       = ""

if __name__ == '__main__':
    graphene = GrapheneClient(Config)

    symbol = "PMS.A"

    asset = graphene.rpc.get_asset(symbol)

    permissions = {"charge_market_fee" : True,
                   "white_list" : True,
                   "override_authority" : True,
                   "transfer_restricted" : True,
                   "disable_force_settle" : True,
                   "global_settle" : True,
                   "disable_confidential" : True,
                   "witness_fed_asset" : True,
                   "committee_fed_asset" : True,
                   }
    flags       = {"charge_market_fee" : False,
                   "white_list" : False,
                   "override_authority" : False,
                   "transfer_restricted" : False,
                   "disable_force_settle" : False,
                   "global_settle" : False,
                   "disable_confidential" : False,
                   "witness_fed_asset" : False,
                   "committee_fed_asset" : False,
                   }
    permissions_int = 0
    for p in permissions :
        if permissions[p]:
            permissions_int += perm[p]
    flags_int = 0
    for p in permissions :
        if flags[p]:
            flags_int += perm[p]
    options = {"max_supply" : 100000000000,
               "market_fee_percent" : 0,
               "max_market_fee" : 0,
               "issuer_permissions" : permissions_int,
               "flags" : flags_int,
               "core_exchange_rate" : {
                   "base": {
                       "amount": 10,
                       "asset_id": "1.3.0"},
                   "quote": {
                       "amount": 10,
                       "asset_id": asset["id"]}},
               "whitelist_authorities" : [],
               "blacklist_authorities" : [],
               "whitelist_markets" : [],
               "blacklist_markets" : [],
               "description" : "My fancy description 2"
               }

    tx = graphene.rpc.update_asset(symbol, None, options, True)
    print(json.dumps(tx, indent=4))
