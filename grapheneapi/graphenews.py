import time
import sys
import json
import asyncio
from functools import partial

try :
    from autobahn.asyncio.websocket import WebSocketClientFactory
except ImportError:
    raise ImportError( "Missing dependency: python-autobahn" )
from grapheneapi import GrapheneAPI, GrapheneWebsocketProtocol

class GrapheneWebsocket(GrapheneAPI):

    """ Constructor takes host, port, and login credentials 
    """
    def __init__(self, host, port, username, password, proto=GrapheneWebsocketProtocol) :
        self.username = username
        self.password = password
        self.host     = host
        self.port     = port
        self.proto    = proto
        self.proto.username = self.username
        self.proto.password = self.password

        ## initialize API (overwrites __getattr__()
        super().__init__(host, port, username, password)

    """ Get an object_id by name
    """
    def object_id(self, name, instance=0) :
        objects = {
            "NULL"                           :  "1.0.%d",
            "BASE"                           :  "1.1.%d",
            "ACCOUNT"                        :  "1.2.%d",
            "FORCE_SETTLEMENT"               :  "1.3.%d",
            "ASSET"                          :  "1.4.%d",
            "DELEGATE"                       :  "1.5.%d",
            "WITNESS"                        :  "1.6.%d",
            "LIMIT_ORDER"                    :  "1.7.%d",
            "CALL_ORDER"                     :  "1.8.%d",
            "CUSTOM"                         :  "1.9.%d",
            "PROPOSAL"                       :  "1.10.%d",
            "OPERATION_HISTORY"              :  "1.11.%d",
            "WITHDRAW_PERMISSION"            :  "1.12.%d",
            "VESTING_BALANCE"                :  "1.13.%d",
            "WORKER"                         :  "1.14.%d",
            "BALANCE"                        :  "1.15.%d",
            "GLOBAL_PROPERTY"                :  "2.0.%d",
            "DYNAMIC_GLOBAL_PROPERTY"        :  "2.1.%d",
            "INDEX_META"                     :  "2.2.%d",
            "ASSET_DYNAMIC_DATA"             :  "2.3.%d",
            "ASSET_BITASSET_DATA"            :  "2.4.%d",
            "DELEGATE_FEEDS"                 :  "2.5.%d",
            "ACCOUNT_BALANCE"                :  "2.6.%d",
            "ACCOUNT_STATISTICS"             :  "2.7.%d",
            "ACCOUNT_DEBT"                   :  "2.8.%d",
            "TRANSACTION"                    :  "2.9.%d",
            "BLOCK_SUMMARY"                  :  "2.10.%d",
            "ACCOUNT_TRANSACTION_HISTORY"    :  "2.11.%d",
            "WITNESS_SCHEDULE"               :  "2.12.%d",
        }
        return objects[name]%instance

    """ Define Callbacks on Objects for websocket connections
    """
    def setObjectCallbacks(self, callbacks) :
        self.proto.database_callbacks = callbacks

    """ Create websocket factory by Autobahn
    """
    def connect(self) :
        self.factory          = WebSocketClientFactory("ws://{}:{:d}".format(self.host, self.port), debug=False)
        self.factory.protocol = self.proto

    """ Store Objects in protocol memory
    """
    def getObject(self, oid) :
        if not (oid in self.proto.objectMap ):
            data = self.get_objects([oid]) 
            if len(data) == 1 :
                self.proto.objectMap[oid] = data[0]
            else :
                self.proto.objectMap[oid] = data
        data = self.proto.objectMap[oid]
        if len(data) == 1 :
            return data[0]
        else :
            return data
            
    """ Run websocket forever and wait for events
    """
    def run_forever(self) :
        loop = asyncio.get_event_loop()
        coro = loop.create_connection(self.factory, self.host, self.port)
        loop.run_until_complete(coro)
        try :
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally :
            loop.close()
