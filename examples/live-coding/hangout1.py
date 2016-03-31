from grapheneapi.grapheneclient import GrapheneClient
from grapheneapi.graphenewsprotocol import GrapheneWebsocketProtocol
from pprint import pprint
from datetime import datetime
import time

class Config(GrapheneWebsocketProtocol):
    # ./programs/cli_wallet/cli_wallet -s ws://127.0.0.1:8090 -H 127.0.0.1:8092
    wallet_host = "localhost"
    wallet_port = 8092
    witness_url = "wss://bitshares.openledger.info/ws"

client = GrapheneClient(Config)
#client.run()

# client.rpc.get_account_by_name("xeroc")




# 1.) establish connection
# 2.) "login"
# 3.) register to apis ('database', 'history', 'network_broadcast')
# 4.) register for notifications of changes to an account
# 5.) register for notifications of changes to a market


quote = client.rpc.get_asset("MKR")
base  = client.rpc.get_asset("OPEN.BTC")

def formatTimeFromNow(secs=0):
    return datetime.utcfromtimestamp(time.time() + int(secs)).strftime('%Y-%m-%dT%H:%M:%S')

pprint(client.ws.get_market_history(quote["id"],
                                    base["id"],
                                    24 * 60 * 60,
                                    formatTimeFromNow(-24 * 60 * 60),
                                    formatTimeFromNow(),
                                    api="history"
                                    ))


# http://docs.bitshares.eu/api/database.html
# http://docs.bitshares.eu/api/history.html

# get_account_history(account, operation_history_id_type stop, unsigned limit, operation_history_id_type start) const
#account = client.rpc.get_account("xeroc")
#pprint(client.ws.get_account_history(account["id"],
#                                     "1.11.0",
#                                     1,
#                                     "1.11.0",
#                                     api="history"))




# * database
# * network_node
# * network_broadcast
# * history
# * crypto




# x.y.z
# x -> 1/2 .. implementation
# y -> object type
# z -> identifier

# 2.0.0 -> global parameters
# 1.2.0 -> committee--account
# pprint(client.getObject("1.3.0"))

# http://docs.bitshares.eu/api/wallet-api.html
#tx = client.rpc.transfer2("xeroc", "fabian", 10, "BTS", "memo", True)
#pprint(tx)
# pprint(client.rpc.get_account_history("xeroc", 2))
# asset = client.rpc.get_asset("USD")
# satoshis = 10000000
# usd = satoshis / 10 ** asset["precision"]
# pprint(asset)
# print(usd)
# pprint(client.getObject('2.3.121'))
