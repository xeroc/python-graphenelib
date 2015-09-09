import time
import sys
import json
import asyncio
from functools import partial
try :
    from autobahn.asyncio.websocket import WebSocketClientProtocol
except ImportError:
    raise ImportError( "Missing dependency: python-autobahn" )

"""
Error Classes
"""
class GrapheneWebsocketProtocol(WebSocketClientProtocol):
    database_callbacks = {}
    database_callbacks_ids = {} # sorted by subscription ids
    objectMap = {}

    def __init__(self) :
        self.request_id = 0
        self.api_ids    = {}
        self.requests   = {}

    def wsexec(self, params, callback=None) :
        request = {"request":{},"callback":None}
        self.request_id += 1
        request["id"] = self.request_id
        request["request"]["id"] = self.request_id
        request["request"]["method"] = "call"
        request["request"]["params"] = params
        request["callback"] = callback
        self.requests.update({self.request_id : request})
        #print(json.dumps(request["request"],indent=4))
        #print(request["request"])
        self.sendMessage(json.dumps(request["request"]).encode('utf8'))

    def _set_api_id(self, name, data) :
        self.api_ids.update({ name : data })

    def _login(self) :
        self.wsexec([1,"login",[self.username,self.password]])

    def getObject(self, oid, callback, *args) :
        if oid in self.objectMap :
            callback(self.objectMap[oid])
        else : 
            handles = [ partial(self.setObject, oid), ]
            if callback : 
                handles.append(callback)
            self.wsexec([self.api_ids["database"],"get_objects", [[oid]]], handles)
            
    def setObject(self, oid, data) :
        self.objectMap[ oid ] = data 

    def subscribe_to_accont(self, account_id, *args) :
        self.wsexec([0, "get_full_accounts", [["1.2."+str(account_id)], True]])

    def subscribe_to_objects(self, *args) :
        handles = []
        for handle in self.database_callbacks :
            handles.append(partial(self.getObject, handle, None))
            self.database_callbacks_ids.update({handle : self.database_callbacks[handle]})
        self.request_id += 1
        self.wsexec([self.api_ids["database"],"set_subscribe_callback", [self.request_id,False]], handles)

    def dispatchNotice(self, notice) :
        oid = notice["id"];
        if oid in self.database_callbacks_ids :
            self.database_callbacks_ids[oid](self, notice)

    ################
    # Websocket API
    ################
    def onConnect(self, response) :
        self.request_id = 1
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        print("WebSocket connection open.")
        self._login()

        """ Register with database
        """
        self.wsexec([1,"database",[]], [
                             partial(self._set_api_id, "database"),
                             self.subscribe_to_objects
                            ])

    def onMessage(self, payload, isBinary):
        res = json.loads(payload.decode('utf8'))
        #print("Server: " + json.dumps(res,indent=1))
        if "error" not in res :
            """ Resolve answers from RPC calls
            """
            if "id" in res :
                if res["id"] not in self.requests :
                    print("Received answer to an unknown request?!")
                else :
                    callbacks = self.requests[res["id"]]["callback"]
                    if callbacks == None :
                        pass
                    elif isinstance(callbacks,list) :
                        for callback in callbacks : 
                            callback(res["result"])
                    else :
                        callbacks(res["result"])
            elif "method" in res :
                """ Run registered call backs for individual object notices
                """
                if res["method"] == "notice" :
                    for notice in res["params"][1][0]:
                        self.setObject(notice["id"], notice)
                        self.dispatchNotice( notice )
        else :
            print("Error! ", res)

    def connection_lost(self) :
        pass

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
