Howto Interface your Exchange with Graphene
===========================================

It is recommended that the developer reads and understands the content of the
following articles:

.. toctree::
   :maxdepth: 2

   graphene-objects
   graphene-api
   graphene-ws
   witness
   wallet
   rpc

Additionally, to get in touch with the implementation details an example script
is provided in :doc:`scripts-monitor`.

Delayed Witness Node
--------------------

Similar to other crypto currencies, it is recommended to wait for several
confirmations of a transcation. Even though the consensus scheme of Graphene is
alot more secure than regular proof-of-work or other proof-of-stake schemes, we
still support exchanges that require more confirmations for deposits.

We provide a so called *delayed* witness node which accepts two additional
parameters for the configuration besides those already available with the
standard daemon (read :doc:`witness`).

* `trusted-node` RPC endpoint of a trusted validating node (required)
* `delay-block-count` Number of blocks to delay before advancing chain state (required)

The trusted-node is a regular witness node directly connected to the P2P
network that works as a proxy. The `delay-block-count` gives the number of
blocks that the delayed witness node will be behind the real blockchain.

Network Setup for this Tutorial
-------------------------------

In the following, we will setup and use the following network:::

    P2P network <-> trusted witness node <-> delayed witness <-> API

For the trusted witness node, the default settings can be used, while for the
delaed witness node we will need to provide the IP address and port of the
p2p-endpoint from the trusted witness node. The delayed witness node will need
to open a RPC/Websocket port (to the local network!) so that we can interface
using RPC-JSON calls.

Note that, for our monitoring script, we will only interface with the delayed
witness.


Interfacing via RPC and Websockets
----------------------------------

In order to access the websocket functionalities, we can extend the
`GrapheneWebsocketProtocol` class. 

.. code-block:: python

    import json
    from grapheneapi import GrapheneWebsocket, GrapheneWebsocketProtocol
    if __name__ == '__main__':
         api = GrapheneWebsocket("localhost", 8090, "", "")
         api.connect()
         api.run_forever()

This example opens up a Websocket connection with localhost on port 8090 with
empty username and passwords and will not do anything.

Subscribing to Account Changes
------------------------------

Let's subscribe to modifications and have it printed out on screen:

.. code-block:: python

     api = GrapheneWebsocket("localhost", 8090, "", "")
     api.setObjectCallbacks({ "2.6.69491" : print })
     api.connect()
     api.run_forever()

The example subscribes to modifications of the object "2.6.69491" and will call
`print` with the notification as parameter.

Hooking Up
----------

To have a more complex interaction with the wallet, we can either make use of
state-less RPC-calls to API-0 or use the websocket connection with callbacks to
access API-1:

* API-0: `api.info()`, `api.get_*()`, ...
* API-1: `api.ws_exec([call], callback)`

To do so, we extend the default `GrapheneWebsocketProtocol` protocol with 

.. code-block:: python

    class GrapheneMonitor(GrapheneWebsocketProtocol) :
        def __init__(self) :
            super().__init__()
        def do_something(self, data) :
            pass
        def do_something_else(self, data) :
            pass

We make use of this class when connecting to the witness node:

.. code-block:: python

        protocol = GrapheneMonitor
        api      = GrapheneWebsocket(host, port, user, password, protocol)

As an example, we can have notifications for all incoming transactions for any account:

.. code-block:: python
    from grapheneapi import GrapheneWebsocket, GrapheneWebsocketProtocol

    class GrapheneMonitor(GrapheneWebsocketProtocol) :
        last_op      = "1.11.0"
        account_id   = "1"
        def __init__(self) :
            super().__init__()

        def printJson(self,d) : print(json.dumps(d,indent=4))

        def onAccountUpdate(self, data) :
            # Get Operation ID that modifies our balance
            opID         = api.getObject(data["most_recent_op"])["operation_id"]
            # self.api_ids["history"] has been defined by the
            # GrapheneWebsocketProtocol and contains the request-id for
            # history_api calls
            self.wsexec([self.api_ids["history"], 
                         "get_account_history",
                         [self.account_id, self.last_op, 100, "1.11.0"]
                        ], self.process_operations)
            self.last_op = opID

        def process_operations(self, operations) :
            for operation in operations[::-1] :
                opID         = operation["id"]
                block        = operation["block_num"]
                op           = operation["op"][1] # [0] contains the operation_type (0: transfers)

                # Get assets involved in Fee and Transfer
                fee_asset    = api.getObject(op["fee"]["asset_id"])
                amount_asset = api.getObject(op["amount"]["asset_id"])

                # Amounts for fee and transfer
                fee_amount   =    op["fee"]["amount"] / float(10**int(fee_asset["precision"]))
                amount_amount= op["amount"]["amount"] / float(10**int(amount_asset["precision"]))

                # Get accounts involved
                from_account = api.getObject(op["from"])
                to_account   = api.getObject(op["to"])

                # Print out
                print("last_op: %s | block:%s | from %s -> to: %s | fee: %f %s | amount: %f %s" % (
                          opID, block, 
                          from_account["name"], to_account["name"],
                          fee_amount, fee_asset["symbol"],
                          amount_amount, amount_asset["symbol"]))

    if __name__ == '__main__':
        """ Account id to monitor """
        accountID = "2.6.69585"
        """ Last operation ID that you have registered in your backend """
        last_op = "1.11.11482"
        """ RPC settings """
        host     = "localhost"
        port     = 8090
        user     = ""
        password = ""
        """ Connection """
        protocol = GrapheneMonitor
        protocol.last_op = last_op ## last operation logged
        protocol.account_id = "1.2.%s" % accountID.split(".")[2]  ## account to monitor
        api      = GrapheneWebsocket(host, port, user, password, protocol)
        api.setObjectCallbacks({accountID : protocol.onAccountUpdate})
        api.connect()
        api.run_forever()

Note, that in order to decode the memo associated with a given transaction, we
need the memo private key.

Decoding the Memo
-----------------

In Graphene, memos are usually encrypted using a distinct memo key. That way,
exposing the memo private key will only expose transaction memos (for that key)
and not compromise any funds. It is thus safe to store the memo private key in
3rd party services and scripts. The memo public key can be obtained from the
account settings or via command line:::

    get_account myaccount

in the cli wallet. The corresponding private key can be obtain from:::

    dump_private_keys

Note that the latter command exposes all private keys in clear-text wif.

The encrypted memo can be decoded with:

.. code-block:: python

    from graphenebase import Memo, PrivateKey, PublicKey
    memo_wif_key = "<wif-key>"
    """ PubKey Prefix
        Productive network: BTS
        Testnetwork: GPH """
    #prefix = "GPH"
    prefix = "BTS"

    memo    = {...} # take from the transfer operation
    privkey = PrivateKey(memo_wif_key)
    pubkey  = PublicKey(memo["from"], prefix=prefix)
    memomsg = Memo.decode_memo(privkey, pubkey, memo["nonce"], memo["message"])

Complete Example
----------------

A full example is provided as `monitor.py` in the `examples/` directory.
