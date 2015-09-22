RPC Interface
=============

We noe need to distinguish functionalities. If we want to only access the
blockchain and do not want to perform on-chain operations like transfers or
orders, we are fine to interface with any accessible witness node. In contrast,
if we want to perform operations that modify the current blockchain state, e.g.
construct and broadcast transactions, we are required to interface with a
cli_wallet that has the required private keys imported. We here assume:

* port: 8090 - witness
* port: 8092 - wallet

RPC-JSON Usage
--------------

All RPC commands of the Graphene client are exposed as methods in the class
grapheneapi. Once an instance of GrapheneAPI is created with host, port,
username, and password, e.g.,::

    from grapheneapi import GrapheneAPI
    rpc = GrapheneAPI("localhost", 8092, "", "")

any (stateless) call can be issued using the instance via the syntax
rpc.*command*(*parameters*). Example:::

    print(json.dumps(rpc.info(),indent=4))

If you are connected to a wallet, you can simply initiate a transfer with:::

    res = client.transfer("sender","receiver","5", "USD", "memo", True);

Again, the witness node does not offer access to construct any transactions,
and hence the calls available to the witness-rpc can be seen as read-only for
the blockchain.

Websocket Usage
---------------

In order to receive notifications of object changes from the witness, we need
to interface with the websockets protocol.

To do so, we have developed a `GrapheneWebsocketProtocol`, an extension to
`WebSocketClientProtocol` as provided by `autobahn.asyncio.websocket`.

In order to access the websocket functionalities, we can extend this class even
further. 

As an example see the provided scripts.
