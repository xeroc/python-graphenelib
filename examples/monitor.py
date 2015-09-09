import sys
import json
from grapheneapi import GrapheneWebsocket, GrapheneWebsocketProtocol

class GrapheneMonitor(GrapheneWebsocketProtocol) :
    def __init__(self) :
        super().__init__()

    def printJson(self,d) : print(json.dumps(d,indent=4))

    def onAccountUpdate(self, data) :
        # most recent operation and callback getTxFromOp
        self.getObject(data["most_recent_op"], self.getTxFromOp)

    def getTxFromOp(self, op) :
        # print the most recent operation for our account!
        self.getObject(op[0]["operation_id"], self.printJson)

if __name__ == '__main__':
     protocol = GrapheneMonitor
     monitor = GrapheneWebsocket("localhost", 8090, "", "", protocol)
     monitor.setObjectCallbacks({
                            "2.6.69491" : protocol.onAccountUpdate,
                           })
     monitor.connect()
     monitor.run_forever()
