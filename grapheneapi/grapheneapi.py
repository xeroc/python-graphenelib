import time
import sys
import json
import asyncio
from functools import partial

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

class GrapheneAPI(object) :
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        
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
        if len(ret["result"]) > 1 :
            return ret["result"]
        else :
            return ret["result"][0]

    """
    Meta: Map all methods to RPC calls and pass through the arguments and result
    """
    def __getattr__(self, name) :
        def method(*args):
            query = {
               "method": "call",
               "params": [0, name, args],
               "jsonrpc": "2.0",
               "id": 0
            }
            r = self.rpcexec(query)
            return r
        return method
