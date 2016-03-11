from grapheneapi.grapheneclient import GrapheneClient
from grapheneapi.graphenewsprotocol import GrapheneWebsocketProtocol
class Config(GrapheneWebsocketProtocol):
    wallet_host           = "localhost"
    wallet_port           = 8092
    witness_url           = "wss://bitshares.openledger.info/ws"
    def onBlock(self, data) :
        print(data)
if __name__ == '__main__':
    r = GrapheneClient(Config)
    r.run()
