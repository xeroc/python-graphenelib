***************
Graphene Client
***************

The ``GrapheneClient`` class is an abstraction layer that makes the use of the
RPC and the websocket interface easier to use. Advanced developers are of course
free to use the underlying API classes instead as well.

Loading of the Library
######################

.. code-block:: python

    from grapheneapi import GrapheneClient, GrapheneWebsocketProtocol

Usage for Wallet RPC only
#########################

The configuration for your connection are defined in a separat class (here
``Config()``):

.. code-block:: python

    class Config():
        wallet_host           = "localhost"
        wallet_port           = 8092
        wallet_user           = ""
        wallet_password       = ""

After opening a connection, the RPC API can be used as follows:

.. code-block:: python

    if __name__ == '__main__':
        graphene = GrapheneClient(Config)
        print(graphene.rpc.info())
        print(graphene.rpc.get_account("init0"))
        print(graphene.rpc.get_asset("USD"))

All methods within ``grapehen.rpc`` are mapped to the corresponding RPC call of
the wallet and the parameters are handed over directly.

Usage with Websockets
#####################

The behavior of your program (e.g. reactions on messages) can be defined in a
separated class (here called ``Config()``. It contains the wallet and witness
connection parameters:

.. code-block:: python

    class Config(GrapheneWebsocketProtocol):  ## Note the dependency
        wallet_host           = "localhost"
        wallet_port           = 8092
        wallet_user           = ""
        wallet_password       = ""
        witness_url           = "ws://localhost:8090/"
        witness_user          = ""
        witness_password      = ""

        watch_accounts        = ["fabian", "nathan"]
        watch_markets         = ["USD:CORE"]

        def onAccountUpdate(self, data):
            [_instance, _type, _id] = data["id"].split(".")
            if _instance == "1" and _type == "2" :
                """
                data = {
                    "most_recent_op": "2.9.252",
                    "pending_fees": 0,
                    "total_core_in_orders": 90000000,
                    "id": "2.6.17",
                    "owner": "1.2.17",
                    "lifetime_fees_paid": "26442269333",
                    "pending_vested_fees": 500000
                }
                """
            elif _instance == "2" and _type == "6" :

                """
                {
                    "options": {
                        "extensions": [],
                        "memo_key": "",
                        "voting_account": "1.2.5",
                        "num_committee": 1,
                        "votes": [
                            "0:11"
                        ],
                        "num_witness": 0
                    },
                    "referrer": "1.2.17",
                    "lifetime_referrer": "1.2.17",
                    "blacklisting_accounts": [],
                    "registrar": "1.2.17",
                    "membership_expiration_date": "1969-12-31T23:59:59",
                    "network_fee_percentage": 2000,
                    "cashback_vb": "1.13.0",
                    "id": "1.2.17",
                    "active": {
                        "weight_threshold": 1,
                        "account_auths": [],
                        "address_auths": [],
                        "key_auths": [
                            [
                                "GPH6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV",
                                1
                            ]
                        ]
                    },
                    "name": "nathan",
                    "referrer_rewards_percentage": 0,
                    "whitelisting_accounts": [],
                    "owner": {
                        "weight_threshold": 1,
                        "account_auths": [],
                        "address_auths": [],
                        "key_auths": [
                            [
                                "GPH6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV",
                                1
                            ]
                        ]
                    },
                    "statistics": "2.6.17",
                    "blacklisted_accounts": [],
                    "lifetime_referrer_fee_percentage": 8000
                }
                """
            pass

        def onMarketUpdate(self, data):
            """
            data = {
                "seller": "1.2.17",
                "id": "1.7.0",
                "for_sale": 88109000,
                "deferred_fee": 0,
                "expiration": "2020-12-23T11:13:42",
                "sell_price": {
                    "base": {
                        "asset_id": "1.3.1",
                        "amount": 100000000
                    },
                    "quote": {
                        "asset_id": "1.3.0",
                        "amount": 1000000000
                    }
                }
            }
            """
            pass

        def onBlock(self, data) :
            """
            data = {
                "id": "2.1.0",
                "dynamic_flags": 0,
                "current_witness": "1.6.7",
                "next_maintenance_time": "2015-12-31T00:00:00",
                "recently_missed_count": 1079135,
                "current_aslot": 345685,
                "head_block_id": "00002f5410b2991a7ed64994b6fe08353603a702",
                "witness_budget": 0,
                "last_irreversible_block_num": 12107,
                "head_block_number": 12116,
                "time": "2015-12-30T10:10:30",
                "accounts_registered_this_interval": 0,
                "recent_slots_filled": "340282366920938463463374607431768211455",
                "last_budget_time": "2015-12-30T09:28:15"
            }
            """
            pass

        def onPropertiesChange(self, data):
            """
            data = { -object-2.0.0- }
            """
            pass

        def onRegisterHistory(self):
            pass

        def onRegisterDatabase(self):
            pass

        def onRegisterNetworkNode(self):
            pass

        def onRegisterNetworkBroadcast(self):
            pass

    if __name__ == '__main__':
        config = Config
        graphene = GrapheneClient(config)
        graphene.run()

The following methods will be called automatically from the underlying websocket
protocol:

.. code-block:: python

        def onBlock(self, data) :
            # Will be called on every new block
        def onPropertiesChange(self, data):
            # Will be called on changes in blockchain parameters

        def onRegisterHistory(self):
            # Will be called when registering the history_api
        def onRegisterDatabase(self):
            # Will be called when registering the database_api

Furthermore, you can register to account and market updates using

.. code-block:: python

        watch_accounts        = ["fabian", "nathan"]
        watch_markets         = ["USD:CORE"]

The corresponding methods that will be called are named

.. code-block:: python

        def onAccountUpdate(self, data):
        def onMarketUpdate(self, data):

.. note:: ``data`` will be the notification from the websocket protocol that
          caused the call. It will have an object id ``data["id"]`` to identify
          it!
