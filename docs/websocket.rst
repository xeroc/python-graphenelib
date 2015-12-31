*********
Websocket
*********

.. note:: This is a low level class that can be used in combination with
          GrapheneClient

In order to receive notifications of object changes from the witness, we need
to interface with the websockets protocol.

To do so, we have developed a `GrapheneWebsocketProtocol`, an extension to
`WebSocketClientProtocol` as provided by `autobahn.asyncio.websocket`.

In order to access the websocket functionalities, we can extend this class even
further. 

.. code-block:: python

    from grapheneapi import GrapheneWebsocket, GrapheneWebsocketProtocol

    class GrapheneMonitor(GrapheneWebsocketProtocol) :
        def __init__(self) :
            super().__init__()

        def onBlock(self, data) :
            print(data)

    if __name__ == '__main__':
        protocol = GrapheneMonitor
        api      = GrapheneWebsocket(config.url, config.user, config.password, protocol)

        ## Set Callback for object changes
        api.setObjectCallbacks({"2.0.0" : protocol.onBlock})

        ## Run the Websocket connection continuously
        api.connect()
        api.run_forever()

Further an examples see the provided scripts.
