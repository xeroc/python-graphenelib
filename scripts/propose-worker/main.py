import json
from grapheneapi import GrapheneAPI
from datetime import datetime
import time
import config

if __name__ == '__main__':

    client = GrapheneAPI(config.wallet_host, config.wallet_port, config.wallet_user, config.wallet_password)
    proposer = client.get_account(config.proposer_account)
    owner    = client.get_account(config.worker_owner)
    asset    = client.get_asset("1.3.0")

    ops = []

    for i in range(0,config.numWorkersPertype) :
        op = client.get_prototype_operation("worker_create_operation")
        op[1]["name"]            = "burn-100k-%d" % (i+1)
        op[1]["owner"]           = owner["id"]
        op[1]["work_begin_date"] = config.start_date
        op[1]["work_end_date"]   = config.end_date
        op[1]["daily_pay"]       = config.daily_pay
        op[1]["url"]             = config.url
        op[1]["initializer"]     =  [
                                      2,{}  # BURN
                                    ]
        ops.append(op)

    for i in range(0,config.numWorkersPertype) :
        op = client.get_prototype_operation("worker_create_operation")
        op[1]["name"]            = "refund-100k-%d" % (i+1)
        op[1]["owner"]           = owner["id"]
        op[1]["work_begin_date"] = config.start_date
        op[1]["work_end_date"]   = config.end_date
        op[1]["daily_pay"]       = config.daily_pay
        op[1]["url"]             = config.url
        op[1]["initializer"]     =  [
                                      0,{}  # Refund
                                    ]
        ops.append(op)

    buildHandle = client.begin_builder_transaction()
    for op in ops :
        client.add_operation_to_builder_transaction(buildHandle, op)
    client.set_fees_on_builder_transaction(buildHandle,asset["id"])

    params = client.get_object("2.0.0")[0]
    preview = params["parameters"]["committee_proposal_review_period"]

    client.propose_builder_transaction2(buildHandle, proposer["name"], config.expiration, preview, False) 
    client.set_fees_on_builder_transaction(buildHandle, asset["id"])

    ## Sign and broadcast
    tx = client.sign_builder_transaction(buildHandle, True)

    print(json.dumps(tx,indent=4))
