from binascii import hexlify, unhexlify
from grapheneapi.grapheneclient import GrapheneClient
import json


fee_paying_account = "xeroc"

data = "Foobar"

class Config():
    wallet_host           = "localhost"
    wallet_port           = 8092
    wallet_user           = ""
    wallet_password       = ""

if __name__ == '__main__':

    graphene = GrapheneClient(Config)
    payer = graphene.rpc.get_account(fee_paying_account)

    op = graphene.rpc.get_prototype_operation("custom_operation")
    op[1]["payer"] = payer["id"]
    op[1]["required_auths"] = [payer["id"]]
    op[1]["data"] = hexlify(bytes(data,'utf-8')).decode('ascii')
    op[1]["id"] = int(16)

    handle = graphene.rpc.begin_builder_transaction()
    graphene.rpc.add_operation_to_builder_transaction(handle, op)
    graphene.rpc.set_fees_on_builder_transaction(handle, "1.3.0")
    tx = graphene.rpc.sign_builder_transaction(handle, False)
    print(json.dumps(tx, indent=4))
