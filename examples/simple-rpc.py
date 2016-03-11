from grapheneapi.grapheneclient import GrapheneClient
from grapheneapi.graphenewsprotocol import GrapheneWebsocketProtocol
import json
from pprint import pprint
from datetime import datetime
import time


class Config(GrapheneWebsocketProtocol):
    wallet_host           = "localhost"
    wallet_port           = 8092
    wallet_user           = ""
    wallet_password       = ""

    witness_url           = "ws://localhost:8090/"
    witness_user          = ""
    witness_password      = ""

    def onRegisterHistory(self):
        print(self)


def formatTimeFromNow(secs=0):
    """ Properly Format Time that is `x` seconds in the future

        :param int secs: Seconds to go in the future (`x>0`) or the
                         past (`x<0`)
        :return: Properly formated time for Graphene (`%Y-%m-%dT%H:%M:%S`)
        :rtype: str

    """
    return datetime.utcfromtimestamp(time.time() + int(secs)).strftime('%Y-%m-%dT%H:%M:%S')

if __name__ == '__main__':
    graphene = GrapheneClient(Config)
    # print(graphene.getObject("2.0.0"))
    # print(graphene.rpc.get_object("2.0.0"))
    # print(graphene.ws.get_object("2.0.0"))
    # account = graphene.rpc.get_account("fabian-secured")
    # print(json.dumps(graphene.ws.get_full_accounts([account["id"]], False), indent=4))

    pprint(graphene.ws.get_market_history("1.3.590",
                                          "1.3.0",
                                          24 * 60 * 60,
                                          formatTimeFromNow(-24 * 60 * 60),
                                          formatTimeFromNow(),
                                          api="history"
                                          ))
