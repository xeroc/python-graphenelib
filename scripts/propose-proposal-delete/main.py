import json
import datetime
from grapheneapi import GrapheneAPI
import config

if __name__ == '__main__':

    client = GrapheneAPI(config.wallet_host, config.wallet_port, config.wallet_user, config.wallet_password)
    proposer = client.get_account(config.proposer_account)
    owner    = client.get_account(config.proposing_account)

    ops = []

    """ Construct TX """
    op                          = client.get_prototype_operation("proposal_delete_operation")
    op[1]["fee_paying_account"] = owner["id"]
    op[1]["proposal"] = config.pid

    ops.append(op)

    buildHandle = client.begin_builder_transaction()
    for op in ops :
        client.add_operation_to_builder_transaction(buildHandle, op)
    client.set_fees_on_builder_transaction(buildHandle, "1.3.0")

    params = client.get_object("2.0.0")[0]
    if owner["name"] == "committee-account":
        preview = params["parameters"]["committee_proposal_review_period"]
    else:
        preview = 0

    delete_proposal = client.get_object(config.pid)[0]
    proposal_preview = datetime.datetime.strptime(delete_proposal["review_period_time"], "%Y-%m-%dT%H:%M:%S")
    expiration = proposal_preview - datetime.timedelta(0, config.expiration_earlier)
    expiration = expiration.strftime('%Y-%m-%dT%H:%M:%S')

    client.propose_builder_transaction2(buildHandle, proposer["name"], expiration, preview, False)
    client.set_fees_on_builder_transaction(buildHandle, "1.3.0")

    """ Sign and broadcast """
    tx = client.sign_builder_transaction(buildHandle, False)
    print(json.dumps(tx, indent=4))

    if client._confirm("Ok for you?") :
        tx = client.sign_builder_transaction(buildHandle, True)
        print(json.dumps(tx, indent=4))
