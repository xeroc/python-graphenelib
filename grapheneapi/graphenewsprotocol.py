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
Graphene Websocket Protocol
"""
class GrapheneWebsocketProtocol(WebSocketClientProtocol):
    loop = None
    database_callbacks = {}
    database_callbacks_ids = {} # sorted by subscription ids
    accounts = []
    accounts_callback = [None]
    objectMap = {}
    onEventCallbacks = {}

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

    def eventcallback(self, name) :
        if name in self.onEventCallbacks and callable(self.onEventCallbacks[name]) :
            self.onEventCallbacks[name](self)

    def _set_api_id(self, name, data) :
        self.api_ids.update({ name : data })
        if name == "database":
            self.eventcallback("registered-database")
        elif name == "history":
            self.eventcallback("registered-history")

    def _login(self) :
        self.wsexec([1,"login",[self.username,self.password]])

    def getObjectcb(self, oid, callback, *args) :
        if oid in self.objectMap and callable(callback):
            callback(self.objectMap[oid])
        else : 
            handles = [ partial(self.setObject, oid), ]
            if callback and callable(callback): 
                handles.append(callback)
            self.wsexec([self.api_ids["database"],"get_objects", [[oid]]], handles)
            
    def setObject(self, oid, data) :
        self.objectMap[ oid ] = data 

    def subscribe_to_accont(self, account_ids, *args) :
        self.wsexec([0, "get_full_accounts", [account_ids, True]])

    def subscribe_to_objects(self, *args) :
        handles = []
        for handle in self.database_callbacks :
            handles.append(partial(self.getObjectcb, handle, None))
            self.database_callbacks_ids.update({handle : self.database_callbacks[handle]})

        if self.accounts :
            handles.append(partial(self.subscribe_to_accont, self.accounts))
        self.request_id += 1
        self.wsexec([self.api_ids["database"],"set_subscribe_callback", [self.request_id,False]], handles)

    def dispatchNotice(self, notice) :
        if not "id" in notice : return
        oid = notice["id"];
        try :
            if oid in self.database_callbacks_ids and callable(self.database_callbacks_ids[oid]):
                self.database_callbacks_ids[oid](self,notice)
            if self.accounts_callback != [None] and callable(self.accounts_callback[0]):
                self.accounts_callback[0](self,notice)
        except Exception as e :
            print('Error dispatching notice: %s' % str(e))

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

        """ Register with history
        """
        self.wsexec([1,"history",[]], [
                             partial(self._set_api_id, "history"),
                            ])

    def onMessage(self, payload, isBinary):
        res = json.loads(payload.decode('utf8'))
        #print("Server: " + json.dumps(res,indent=1))
        #print("\n\nServer: " + str(res))
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
                        if "id" in notice :
                            self.setObject(notice["id"], notice)
                            self.dispatchNotice( notice )
                        else :
                            #print("Warning: Received a notice without id: " + str(notice));
                            pass # FIXME: get this object id
        else :
            print("Error! ", res)

    def setLoop(self,loop) :
        self.loop = loop

    def connection_lost(self, errmsg) :
        print("WebSocket connection closed: {0}".format(errmsg))
        self.loop.stop()
