RPC Interface
=============

Requirements
------------

* python-requests

Configuration
-------------

The Graphene client needs the RPC interface enabled and username, password,
and port set. The relevant port for this module is the port of the
``httpd_endpoint``. Two ways exist to do so:

* Command-line parameters:

.. code-block:: bash

    ./graphene_client --server --httpport 5000 --rpcuser test --rpcpassword test

* Configuration file settings:

.. code-block:: json 

    "rpc": {
         "enable": true,
         "rpc_user": "USERNAME",
         "rpc_password": "PASSWORD",
         "rpc_endpoint": "127.0.0.1:9988",
         "httpd_endpoint": "127.0.0.1:19988", <<--- PORT
         "htdocs": "./htdocs"
         }

Usage
-----
All RPC commands of the Graphene client are exposed as methods in the class
graphenerpc. Once an instance of graphenerpc is created, i.e.,::

    import graphenelib
    rpc = graphenelib.client("http://localhost:19988/rpc", "username","password")

any rpc command can be issued using the instance via the syntax
rpc.*command*(*parameters*). Example:::

    print(json.dumps(rpc.getinfo(),indent=4))
    print(json.dumps(rpc.about()  ,indent=4))

    rpc.open_wallet("default")
    rpc.ask(account, amount, quote, price, base)

Unlocking a wallet
------------------
The ``unlock`` call is overwritten by the library. It takes as a first argument
the timeout (in seconds) until the wallet is relocked automatically by the client and as an
optional second argument the passphrase of the wallet. ::

    rpc.unlock(3600)

.. note::

        If no (or an empty) passphrase is given AND the wallet is locked, the
        library will ask to manually provide a passphrase.

Exceptions
----------

``UnauthorizedError(Exception)``
  Is thrown if login credentials are invalid.
``RPCError(Exception)``
  Is thrown if the Graphene client returns an error.
``RPCConnection(Exception)``
  Is thrown if no connection can be established
