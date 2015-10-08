import time
import json
from grapheneapi import GrapheneAPI

blockinterval    = 5
numbertxperblock = 15

if __name__ == '__main__':
    client = GrapheneAPI("localhost", 8092, "", "")
    while True :
        for i in range(0,numbertxperblock) :
            print(i)
            res = client.transfer("fabian.schuh","schuh","0.00001", "CORE", "memo", True);
            print(json.dumps(res,indent=4))
        time.sleep(blockinterval)
