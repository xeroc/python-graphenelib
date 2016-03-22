from websocket import create_connection
import json


class RPCError(Exception):
    pass


class GrapheneWebsocketRPC(object):
    """ This class allows to call API methods synchronously, without
        callbacks. It logs in and registers to the APIs:

        * database
        * history

        :param str url: Websocket URL
        :param str user: Username for Authentication
        :param str password: Password for Authentication

        Usage:

        .. code-block:: python

            ws = GrapheneWebsocketRPC("ws://10.0.0.16:8090","","")
            print(ws.get_account_count())

        .. note:: This class allows to call methods available via
                  websocket. If you want to use the notification
                  subsystem, please use ``GrapheneWebsocket`` instead.

    """
    call_id = 0
    api_id = {}

    def __init__(self, url, user="", password=""):
        self.url = url
        self.user = user
        self.password = password
        self.ws = create_connection(url)
        self.login("", "", api_id=1)
        self.api_id["database"] = self.database(api_id=1)
        self.api_id["history"] = self.history(api_id=1)
        self.api_id["network_broadcast"] = self.network_broadcast(api_id=1)

    def get_call_id(self):
        """ Get the ID for the next RPC call """
        self.call_id += 1
        return self.call_id

    def get_account(self, name):
        if "." in name:
            return self.get_objects([name])[0]
        else :
            return self.get_account_by_name(name)

    def get_asset(self, name):
        if "." in name:
            return self.get_objects([name])[0]
        else :
            return self.lookup_asset_symbols([name])[0]

    def rpcexec(self, payload):
        """ Execute a call by sending the payload

            :param json payload: Payload data
            :raises ValueError: if the server does not respond in proper JSON format
            :raises RPCError: if the server returns an error
        """
        try:
            self.ws.send(json.dumps(payload))
            ret = json.loads(self.ws.recv())
            if 'error' in ret:
                if 'detail' in ret['error']:
                    raise RPCError(ret['error']['detail'])
                else:
                    raise RPCError(ret['error']['message'])
        except ValueError:
            raise ValueError("Client returned invalid format. Expected JSON!")
        except RPCError as err:
            raise err
        else:
            return ret["result"]

    def __getattr__(self, name):
        """ Map all methods to RPC calls and pass through the arguments
        """
        def method(*args, **kwargs):
            if "api_id" not in kwargs :
                if ("api" in kwargs and kwargs["api"] in self.api_id) :
                    api_id = self.api_id[kwargs["api"]]
                else:
                    api_id = 0
            else:
                api_id = kwargs["api_id"]
            query = {"method": "call",
                     "params": [api_id, name, args],
                     "jsonrpc": "2.0",
                     "id": 0}
            r = self.rpcexec(query)
            return r
        return method
