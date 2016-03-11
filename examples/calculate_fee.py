from grapheneapi.grapheneclient import GrapheneClient
from pprint import pprint

class Config():
    wallet_host       = "localhost"
    wallet_port       = 8092
    witness_url       = "wss://bitshares.openledger.info/ws"


if __name__ == '__main__':
    client = GrapheneClient(Config)
    op = client.rpc.get_prototype_operation("limit_order_create_operation")
    pprint(client.ws.get_required_fees([op], "1.3.0"))
