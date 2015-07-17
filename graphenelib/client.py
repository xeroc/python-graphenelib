import time
import sys
import json
import asyncio
from functools import partial
try :
    from autobahn.asyncio.websocket import WebSocketClientProtocol, \
        WebSocketClientFactory
except ImportError:
    raise ImportError( "Missing dependency: python-autobahn" )
try :
    import requests
except ImportError:
    raise ImportError( "Missing dependency: python-requests" )

"""
Error Classes
"""
class UnauthorizedError(Exception) :
    pass

class RPCError(Exception) :
    pass

class RPCConnection(Exception) :
    pass

class GrapheneWebsocketProtocol(WebSocketClientProtocol):
    database_callbacks = []

    def __init__(self) :
        self.request_id = None
        self.api_ids    = {}
        self.requests   = {}

    def setObjectCallbacks(self, callbacks) :
        self.database_callbacks = callbacks

    def onConnect(self, response) :
        self.request_id = 1
        print("Server connected: {0}".format(response.peer))

    def rpcexec(self, params, callback=None) :
        request = {"request":{},"callback":None}
        self.request_id += 1
        request["id"] = self.request_id
        request["request"]["id"] = self.request_id
        request["request"]["method"] = "call"
        request["request"]["params"] = params
        request["callback"] = callback
        self.requests.update({self.request_id : request})
        self.sendMessage(json.dumps(request["request"]).encode('utf8'))

    def _set_api_id(self, name, data) :
        self.api_ids.update({ name : data["result"] })

    def _login(self) :
        self.rpcexec([1,"login",[self.username,self.password]])

    def subscribe_to_objects(self, objs, data) :
        self.rpcexec([self.api_ids["database"],"subscribe_to_objects", objs])

    def onOpen(self):
        print("WebSocket connection open.")
        self._login()

        """ Register with network_broadcast
        """
        self.rpcexec([1,"network_broadcast",[]], [\
                     partial(self._set_api_id, "network_broadcast"),
                 ])

        """ Register with database and subscribe to objects
        """
        handles = [partial(self._set_api_id, "database")]
        for i,handle in enumerate(self.database_callbacks) :
            handles.append(partial(self.subscribe_to_objects, [i,[handle]]))
        self.rpcexec([1,"database",[]], handles)

    def onMessage(self, payload, isBinary):
        res = json.loads(payload.decode('utf8'))
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
                            callback(res)
                    else :
                        callbacks(res)
            elif "method" in res :
                """ Run registered call backs for individual object notices
                """
                if res["method"] == "notice" :
                    callbackID = res["params"][0]
                    callbackhandler = list(self.database_callbacks.values())[callbackID]
                    callbackhandler(res["params"][1])
        else :
            print("Error! ", res)

    def connection_lost(self) :
        pass

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))

class GrapheneClient(object):
    """ Constructor takes host, port, and login credentials 
    """
    def __init__(self, host, port, username, password) :
        self.username = username
        self.password = password
        self.host     = host
        self.port     = port
        self.headers = {'content-type': 'application/json'}

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
        self.proto = GrapheneWebsocketProtocol
        self.proto.username = self.username
        self.proto.password = self.password
        self.proto.database_callbacks = callbacks

    """ Create websocket factory by Autobahn
    """
    def connect(self) :
        self.factory          = WebSocketClientFactory("ws://{}:{:d}".format(self.host, self.port), debug=False)
        self.factory.protocol = self.proto

    """ Run websocket forever and wait for events
    """
    def run_forever(self) :
        loop = asyncio.get_event_loop()
        coro = loop.create_connection(self.factory, self.host, self.port)
        loop.run_until_complete(coro)
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            loop.close()

    """ Manual execute a command on API
    """
    def rpcexec(self,payload) :
        try : 
            response = requests.post("http://{}:{}/rpc".format(self.host,self.port),
                                     data=json.dumps(payload),
                                     headers=self.headers,
                                     auth=(self.username,self.password))
            if response.status_code == 401 :
                raise UnauthorizedError
            ret = json.loads(response.text)
            if 'error' in ret :
                if 'detail' in ret['error']:
                    raise RPCError(ret['error']['detail'])
                else:
                    raise RPCError(ret['error']['message'])
        except requests.exceptions.RequestException :
            raise RPCConnection("Error connecting to Client. Check hostname and port!")
        except UnauthorizedError :
            raise UnauthorizedError("Invalid login credentials!")
        except ValueError :
            raise ValueError("Client returned invalid format. Expected JSON!")
        except RPCError as err:
            raise err

        return ret["result"] # Return only the result

    def login(self) :
       r = self.rpcexec({
           "method": "call",
           "params": [1, "login", [self.username, self.password]],
           "jsonrpc": "2.0",
           "id": 0
       })
       assert r, UnauthorizedError("Invalid login credentials!")
       return r

    """
    Meta: Map all methods to RPC calls and pass through the arguments and result
    """
    def __getattr__(self, name) :
        def method(*args):
           r = self.rpcexec({
               "method": "call",
               "params": [0, name, [args]],
               "jsonrpc": "2.0",
               "id": 0
           })
           return r
        return method

if __name__ == '__main__':
    rpc = GrapheneClient("localhost", 8090, "","")
    print(json.dumps(rpc.login(),indent=4))
    print(json.dumps(rpc.get_accounts("1.2.0"),indent=4))
