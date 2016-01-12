***************************
Simple Bridge Market Making
***************************

.. note:: This script serves as a tutorial on how to program an
          automated trading machine for BitShares that makes markets
          that should trade at parity (e.g. BTC:OPENBTC). Please read
          the LICENSE.

Configuration
#############

1. We need to setup the :doc:`wallet` and enable RPC.
2. Either Run your own :doc:`witness` or identify a public Websocket API
3. Configuration of the script:
   To configure, we need to open the file
   ``scripts/exchange-bridge-market-maker``:

   * Wallet connection settings (at least host and port)
   * Witness connection (witness url)
   * ``watch_markets``: an array of markets that should trade at parity
     and will be used to place orders (if funds are available)
   * ``market_separator``: The string that is used to separated assets
     in the markets
   * ``account``: The BTS account that should be used for placing
     orders.
   * ``bridge_spread_percent``: The spread at which orders will be
     placed (prices: +-spread/2)
   * ``bridge_amount_percent``: The **total** amounts that should be
     held in orders as a percentage.

Running
#######

The script is implemented to automatically cancel all of your orders in
the *watched* markets and place new orders.

.. code-block:: sh

    $ python3 main.py

Hence, it makes sense to create a new account that serves as a
bot-account and run the script frequently (e.g. via a *crontjob*).

.. code-block:: cron

    * * * */2 0 python3 /path/to/main.py
