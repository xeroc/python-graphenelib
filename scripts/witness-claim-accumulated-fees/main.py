import json
from grapheneapi import GrapheneAPI
import math
import config

if __name__ == '__main__':

    client = GrapheneAPI(config.wallet_host, config.wallet_port, config.wallet_user, config.wallet_password)
    proposer = client.get_account(config.proposer_account)
    owner    = client.get_account(config.issuer_account)

    ops = []

    for symbol in config.claim_assets :
        percentage = config.claim_assets[symbol]
        asset      = client.get_asset(symbol)

        """ Construct TX """
        op                       = client.get_prototype_operation("asset_claim_fees_operation")
        op[1]["issuer"]          = owner["id"]
        op[1]["amount_to_claim"]["asset_id"] = asset["id"]

        """ Get accumulated amount from blockchain """
        asset_data = client.get_object(asset["dynamic_asset_data_id"])[0]
        accumulated_fees = asset_data["accumulated_fees"]
        op[1]["amount_to_claim"]["amount"] = math.floor(accumulated_fees * percentage)

        ops.append(op)

    buildHandle = client.begin_builder_transaction()
    for op in ops :
        client.add_operation_to_builder_transaction(buildHandle, op)
    client.set_fees_on_builder_transaction(buildHandle,asset["id"])

    params = client.get_object("2.0.0")[0]
    if owner["name"] == "committee-account":
        preview = params["parameters"]["committee_proposal_review_period"]
    else:
        preview = 0

    client.propose_builder_transaction2(buildHandle, proposer["name"], config.expiration, preview, False) 
    client.set_fees_on_builder_transaction(buildHandle, asset["id"])

    ## Sign and broadcast
    tx = client.sign_builder_transaction(buildHandle, False)
    print(json.dumps(tx,indent=4))

    if client._confirm("Ok for you?") :
        tx = client.sign_builder_transaction(buildHandle, True)
        print(json.dumps(tx,indent=4))
