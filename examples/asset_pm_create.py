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
GRAPHENE_100_PERCENT = 10000
GRAPHENE_1_PERCENT = GRAPHENE_100_PERCENT / 100


class Config():
    wallet_host           = "localhost"
    wallet_port           = 8092
    wallet_user           = ""
    wallet_password       = ""

if __name__ == '__main__':
    graphene = GrapheneClient(Config)

    issuer = "nathan"
    symbol = "PMS.A"
    backing = "1.3.0"

    account = graphene.rpc.get_account(issuer)
    asset = graphene.rpc.get_asset(backing)

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
                   "disable_force_settle" : True,
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
    options = {"max_supply" : 10000000000,
               "market_fee_percent" : 0,
               "max_market_fee" : 0,
               "issuer_permissions" : permissions_int,
               "flags" : flags_int,
               "core_exchange_rate" : {
                   "base": {
                       "amount": 10,
                       "asset_id": asset["id"]},
                   "quote": {
                       "amount": 10,
                       "asset_id": "1.3.1"}},
               "whitelist_authorities" : [],
               "blacklist_authorities" : [],
               "whitelist_markets" : [],
               "blacklist_markets" : [],
               "description" : "Prediction Market"
               }
    mpaoptions = {"feed_lifetime_sec" : 60 * 15,
                  "minimum_feeds" : 1,
                  "force_settlement_delay_sec" : 10,
                  "force_settlement_offset_percent" : 0 * GRAPHENE_1_PERCENT,
                  "maximum_force_settlement_volume" : 100 * GRAPHENE_1_PERCENT,
                  "short_backing_asset" : asset["id"],
                  }

    op = graphene.rpc.get_prototype_operation("asset_create_operation")
    op[1]["issuer"] = account["id"]
    op[1]["symbol"] = symbol
    op[1]["precision"] = asset["precision"]
    op[1]["common_options"] = options
    op[1]["is_prediction_market"] = True
    op[1]["bitasset_opts"] = mpaoptions
    print(op)

    handle = graphene.rpc.begin_builder_transaction()
    graphene.rpc.add_operation_to_builder_transaction(handle, op)
    graphene.rpc.set_fees_on_builder_transaction(handle, "1.3.0")
    tx = graphene.rpc.sign_builder_transaction(handle, True)
    print(json.dumps(tx, indent=4))
