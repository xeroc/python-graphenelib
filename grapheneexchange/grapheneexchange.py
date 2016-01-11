from grapheneapi import GrapheneClient
from datetime import datetime
import time
import json


class ExampleConfig() :
    """ The behavior of your program can be
        defined in a separated class (here called ``ExampleConfig()``. It
        contains the wallet and witness connection parameters:

        The config class is used to define several attributes *and*
        methods that will be used during API communication..


        **Additional Websocket Connections**:

        .. code-block:: python

            class Config(GrapheneWebsocketProtocol):  ## Note the dependency
                wallet_host           = "localhost"
                wallet_port           = 8092
                wallet_user           = ""
                wallet_password       = ""
                witness_url           = "ws://localhost:8090/"
                witness_user          = ""
                witness_password      = ""

        All methods within ``graphene.rpc`` are mapped to the
        corresponding RPC call of the wallet and the parameters are
        handed over directly. Similar behavior is implemented for
        ``graphene.ws`` which can deal with calls to the witness node.

        This allows the use of rpc commands similar to the
        ``GrapheneAPI`` class:

        .. code-block:: python

            graphene = GrapheneExchange(Config)
            # Calls to the cli-wallet
            print(graphene.rpc.info())
            print(graphene.rpc.get_account("init0"))
            print(graphene.rpc.get_asset("USD"))
            # Calls to the witness node
            print(ws.get_account_count())

    """

    #: Wallet connection parameters
    wallet_host           = "localhost"
    wallet_port           = 8092
    wallet_user           = ""
    wallet_password       = ""

    #: Witness connection parameter
    witness_url           = "ws://localhost:8090/"
    witness_user          = ""
    witness_password      = ""

    #: The account used here
    account               = "fabian"

    #: Markets to watch.
    watch_markets         = ["USD_BTS"]
    market_separator      = "_"


class GrapheneExchange(GrapheneClient) :
    """ This class serves as an abstraction layer for the decentralized
        exchange within the network and simplifies interaction for
        trading bots.

        :param config config: Configuration Class, similar to the
                              example above

        This class tries to map the poloniex API around the DEX but has
        some differences:

            * market pairs are denoted as 'quote'_'base', e.g. `USD_BTS`
            * Prices/Rates are denoted in 'quote', i.e. the USD_BTS market
              is priced in USD and buying 1 USD costs `rate` BTS
            * All markets could be considered reversed as well ('BTS_USD')

        Usage:

        .. code-block:: python


            from grapheneexchange import GrapheneExchange
            import json


            class Config():
                wallet_host           = "localhost"
                wallet_port           = 8092
                wallet_user           = ""
                wallet_password       = ""
                witness_url           = "ws://10.0.0.16:8090/"
                witness_user          = ""
                witness_password      = ""

                watch_markets         = ["USD_BTS", "GOLD_BTS"]
                market_separator      = "_"
                account               = "mindphlux"

            if __name__ == '__main__':
                dex   = GrapheneExchange(Config)
                print(json.dumps(dex.returnTradeHistory("USD_BTS"),indent=4))
                print(json.dumps(dex.returnTicker(),indent=4))
                print(json.dumps(dex.return24Volume(),indent=4))
                print(json.dumps(dex.returnOrderBook("USD_BTS"),indent=4))
                print(json.dumps(dex.returnBalances(),indent=4))
                print(json.dumps(dex.returnOpenOrders("all"),indent=4))
                print(json.dumps(dex.buy("USD_BTS", 0.001, 10),indent=4))
                print(json.dumps(dex.sell("USD_BTS", 0.001, 10),indent=4))
    """
    markets = {}
    account = ""
    wallet = None

    def __init__(self, config) :
        self.config = config
        super().__init__(config)

    def formatTimeFromNow(self, secs=0):
        """ Properly Format Time that is `x` seconds in the future

            :param int secs: Seconds to go in the future (`x>0`) or the
                             past (`x<0`)
            :return: Properly formated time for Graphene (`%Y-%m-%dT%H:%M:%S`)
            :rtype: str

        """
        return datetime.utcfromtimestamp(time.time() + int(secs)).strftime('%Y-%m-%dT%H:%M:%S')

    def _get_price(self, o) :
        """ Given an object with `quote` and `base`, derive the correct
            price.

            Prices/Rates are denoted in 'quote', i.e. the USD_BTS market
            is priced in USD and buying 1 USD costs `rate` BTS
        """
        quote_amount = float(o["quote"]["amount"])
        base_amount  = float(o["base"]["amount"])
        quote_id     = o["quote"]["asset_id"]
        base_id      = o["base"]["asset_id"]
        quote, base  = self.ws.get_objects([quote_id, base_id])
        return float((quote_amount / 10 ** quote["precision"]) /
                     (base_amount / 10 ** base["precision"]))

    def _get_price_filled(self, f, m):
        """ A filled order has `receives` and `pays` ops which serve as
            `base` and `quote` depending on sell or buy
        """
        r = {}
        if f["op"]["receives"]["asset_id"] == m["base"] :
            # If the seller received "base" in a quote_base market, than
            # it has been a sell order of quote
            r["base"] = f["op"]["receives"]
            r["quote"] = f["op"]["pays"]
        else:
            # buy order
            r["base"] = f["op"]["pays"]
            r["quote"] = f["op"]["receives"]
        return self._get_price(r)

    def returnCurrencies(self):
        """ In contrast to poloniex, this call returns the assets of the
            watched markets only.

            Example Output:

            .. code-block:: json

            {'BTS': {'issuer': '1.2.3', 'id': '1.3.0', 'dynamic_asset_data_id': '2.3.0', 'precision': 5, 'symbol': 'BTS', 'options': {'max_market_fee': '1000000000000000', 'blacklist_authorities': [], 'blacklist_markets': [], 'description': '', 'whitelist_authorities': [], 'market_fee_percent': 0, 'core_exchange_rate': {'base': {'asset_id': '1.3.0', 'amount': 1}, 'quote': {'asset_id': '1.3.0', 'amount': 1}}, 'flags': 0, 'extensions': [], 'whitelist_markets': [], 'issuer_permissions': 0, 'max_supply': '360057050210207'}}, 'GOLD': {'issuer': '1.2.0', 'id': '1.3.106', 'dynamic_asset_data_id': '2.3.106', 'precision': 6, 'bitasset_data_id': '2.4.6', 'symbol': 'GOLD', 'options': {'max_market_fee': '1000000000000000', 'blacklist_authorities': [], 'blacklist_markets': [], 'description': '1 troy ounce .999 fine gold', 'whitelist_authorities': [], 'market_fee_percent': 0, 'core_exchange_rate': {'base': {'asset_id': '1.3.106', 'amount': 1}, 'quote': {'asset_id': '1.3.0', 'amount': 34145}}, 'flags': 128, 'extensions': [], 'whitelist_markets': [], 'issuer_permissions': 511, 'max_supply': '1000000000000000'}}, 'USD': {'issuer': '1.2.0', 'id': '1.3.121', 'dynamic_asset_data_id': '2.3.121', 'precision': 4, 'bitasset_data_id': '2.4.21', 'symbol': 'USD', 'options': {'max_market_fee': '1000000000000000', 'blacklist_authorities': [], 'blacklist_markets': [], 'description': '1 United States dollar', 'whitelist_authorities': [], 'market_fee_percent': 0, 'core_exchange_rate': {'base': {'asset_id': '1.3.121', 'amount': 5}, 'quote': {'asset_id': '1.3.0', 'amount': 15751}}, 'flags': 128, 'extensions': [], 'whitelist_markets': [], 'issuer_permissions': 511, 'max_supply': '1000000000000000'}}}

        """
        r = {}
        asset_ids = []
        for market in self.markets :
            m = self.markets[market]
            asset_ids.append(m["base"])
            asset_ids.append(m["quote"])
        asset_ids_unique = list(set(asset_ids))
        assets = self.ws.get_objects(asset_ids_unique)
        for a in assets:
            r.update({a["symbol"] : a})
        return r

    def returnTicker(self):
        """ Returns the ticker for all markets.

            Sample Output:

            .. code-block:: json

                {
                    "GOLD_BTS": {
                        "baseVolume": 0,
                        "last": 2.2831050228310503e-05,
                        "lowestAsk": 2.25e-05,
                        "highestBid": 2.0833333333333333e-05,
                        "quoteVolume": 0,
                        "percentChange": 0
                    },
                    "USD_BTS": {
                        "baseVolume": 36166663617.0,
                        "last": 0.0003787878787878788,
                        "lowestAsk": 0.0003787878787878788,
                        "highestBid": 0.0003676470588235294,
                        "quoteVolume": 10870000.0,
                        "percentChange": 26.893939393939405
                    }
                }
        """
        r = {}
        for market in self.markets :
            m = self.markets[market]
            marketHistory = self.ws.get_market_history(
                m["quote"], m["base"],
                24 * 60 * 60,
                self.formatTimeFromNow(-24 * 60 * 60),
                self.formatTimeFromNow(),
                api="history")
            orders = self.rpc.get_limit_orders(
                m["quote"], m["base"], 1)
            filled = self.ws.get_fill_order_history(
                m["quote"], m["base"], 0, api="history")[0]
            quote_asset, base_asset = self.ws.get_objects([m["quote"], m["base"]])
            pricelast = self._get_price_filled(filled, m)
            data = {}
            data["last"]          = pricelast
            data["lowestAsk"]     = self._get_price(orders[1]["sell_price"])
            data["highestBid"]    = (1 / self._get_price(orders[0]["sell_price"]))
            if len(marketHistory) :
                if marketHistory[0]["key"]["quote"] == m["quote"] :
                    data["baseVolume"]    = float(marketHistory[0]["base_volume"])  / (10 ** base_asset["precision"])
                    data["quoteVolume"]   = float(marketHistory[0]["quote_volume"]) / (10 ** quote_asset["precision"])
                    price24h = ((float(marketHistory[0]["open_quote"]) / 10 ** quote_asset["precision"]) /
                                (float(marketHistory[0]["open_base"])  / 10 ** base_asset["precision"]))
                else :
                    #: Looks weird but is correct:
                    data["baseVolume"]    = float(marketHistory[0]["quote_volume"]) / (10 ** base_asset["precision"])
                    data["quoteVolume"]   = float(marketHistory[0]["base_volume"])  / (10 ** quote_asset["precision"])
                    price24h = ((float(marketHistory[0]["open_base"])  / 10 ** quote_asset["precision"]) /
                                (float(marketHistory[0]["open_quote"]) / 10 ** base_asset["precision"]))
                data["percentChange"] = ((pricelast / price24h - 1) * 100)
                data["price24hago"] = price24h
            else :
                data["baseVolume"]    = 0
                data["quoteVolume"]   = 0
                data["percentChange"] = 0
            r.update({market : data})
        return r

    def return24Volume(self):
        """ Returns the 24-hour volume for all markets, plus totals for primary currencies.

            Sample output:

            .. code-block:: json

                {
                    "USD_BTS": {
                        "BTS": 361666.63617,
                        "USD": 1087.0
                    },
                    "GOLD_BTS": {
                        "BTS": 0,
                        "GOLD": 0
                    }
                }

        """
        r = {}
        for market in self.markets :
            m = self.markets[market]
            marketHistory = self.ws.get_market_history(
                m["quote"], m["base"],
                24 * 60 * 60,
                self.formatTimeFromNow(-24 * 60 * 60),
                self.formatTimeFromNow(),
                api="history")
            quote_asset, base_asset = self.ws.get_objects([m["quote"], m["base"]])
            data = {}
            if len(marketHistory) :
                if marketHistory[0]["key"]["quote"] == m["quote"] :
                    data[m["base_symbol"]] = float(marketHistory[0]["base_volume"]) / (10 ** base_asset["precision"])
                    data[m["quote_symbol"]] = float(marketHistory[0]["quote_volume"]) / (10 ** quote_asset["precision"])
                else :
                    data[m["base_symbol"]] = float(marketHistory[0]["quote_volume"]) / (10 ** base_asset["precision"])
                    data[m["quote_symbol"]] = float(marketHistory[0]["base_volume"]) / (10 ** quote_asset["precision"])
            else :
                data[m["base_symbol"]] = 0
                data[m["quote_symbol"]] = 0
            r.update({market : data})
        return r

    def returnOrderBook(self, currencyPair="all", limit=25):
        """ Returns the order book for a given market. You may also
            specify "all" to get the orderbooks of all markets.

            :param str currencyPair: Return results for a particular market only (default: "all")
            :param int limit: Limit the amount of orders (default: 25)

            Ouput is formated as:::

                [price, amount]

            * price is denoted in quote
            * amount is in quote

            Sample output:

            .. code-block:: json

                {'USD_BTS': {'asks': [[0.0003787878787878788, 203.1935],
                [0.0003799587270281197, 123.65374999999999]], 'bids':
                [[0.0003676470588235294, 9.9], [0.00036231884057971015,
                10.0]]}, 'GOLD_BTS': {'asks': [[2.25e-05,
                0.045000000000000005], [2.3408239700374533e-05,
                0.33333333333333337]], 'bids': [[2.0833333333333333e-05,
                0.4], [1.851851851851852e-05, 0.0001]]}}

            If a single market is chosen, the returning format is
            slightly smaller:

            .. code-block:: json

                {'bids': [[0.0003676470588235294, 9.9],
                [0.00036231884057971015, 10.0]], 'asks':
                [[0.0003787878787878788, 203.1935],
                [0.0003799587270281197, 123.65374999999999]]}

            .. note:: A maximum of 25 orders will be returned!

        """
        r = {}
        if currencyPair == "all" :
            markets = list(self.markets.keys())
        else:
            markets = [currencyPair]
        for market in markets :
            m = self.markets[market]
            orders = self.ws.get_limit_orders(
                m["quote"], m["base"], limit)
            quote_asset, base_asset = self.ws.get_objects([m["quote"], m["base"]])
            asks = []
            bids = []
            for o in orders:
                if o["sell_price"]["base"]["asset_id"] == m["base"] :
                    price = self._get_price(o["sell_price"])
                    volume = float(o["for_sale"]) / 10 ** base_asset["precision"] * self._get_price(o["sell_price"])
                    asks.append([price, volume])
                else :
                    price = 1 / self._get_price(o["sell_price"])
                    volume = float(o["for_sale"]) / 10 ** quote_asset["precision"]
                    bids.append([price, volume])

            data = {"asks" : asks, "bids" : bids}
            r.update({market : data})
        if len(markets) == 1 :
            return r[markets[0]]
        else:
            return r

    def returnBalances(self):
        """ Returns all of your balances.

            Example Output:

            .. code-block:: json

                {
                    "BROWNIE.PTS": 2499.9999,
                    "EUR": 0.0028,
                    "BTS": 1893552.94893,
                    "OPENBTC": 0.00110581,
                    "GREENPOINT": 0.0
                }

            .. note:: Zero balance assets are included!

        """
        account = self.rpc.get_account(self.config.account)
        balances = self.ws.get_account_balances(account["id"], [])
        asset_ids = [a["asset_id"] for a in balances]
        assets = self.ws.get_objects(asset_ids)
        data = {}
        for i, asset in enumerate(assets) :
            data[asset["symbol"]] = float(balances[i]["amount"]) / 10 ** asset["precision"]
        return data

    def returnOpenOrders(self, currencyPair="all"):
        """ Returns your open orders for a given market, specified by
            the "currencyPair.

            Output Parameters:

                - `type`: sell or buy
                - `rate`: price for `quote` denoted in `base` ($50c per BTS = 0.5 USD/BTS)
                - `orderNumber`: identifier (e.g. for cancelation)
                - `amount`: amount of quote
                - `total`: amount of base at asked price (amount/price)

            Example Output:

            .. code-block:: json

                {
                    "USD_BTS": [
                        {
                            "total": 0.003639705882352941,
                            "type": "buy",
                            "rate": 0.0003676470588235294,
                            "orderNumber": "1.7.18646",
                            "amount": 9.9
                        },
                        {
                            "total": 0.0036231884057971015,
                            "type": "buy",
                            "rate": 0.00036231884057971015,
                            "orderNumber": "1.7.18644",
                            "amount": 10.0
                        }
                    ],
                    "GOLD_BTS": []
                }

            .. note:: Ths method will not show orders of markets that
                      are **not** in the ``watch_markets`` array!
        """
        account = self.rpc.get_account(self.config.account)
        r = {}
        if currencyPair == "all" :
            markets = list(self.markets.keys())
        else:
            markets = [currencyPair]
        orders = self.ws.get_full_accounts([account["id"]], False)[0][1]["limit_orders"]
        for market in markets :
            r[market] = []
        for o in orders:
            quote_id = o["sell_price"]["quote"]["asset_id"]
            base_id = o["sell_price"]["base"]["asset_id"]
            quote_asset, base_asset = self.ws.get_objects([quote_id, base_id])
            for market in markets :
                m = self.markets[market]
                if (o["sell_price"]["base"]["asset_id"] == m["base"] and
                        o["sell_price"]["quote"]["asset_id"] == m["quote"]):
                    " selling "
                    amount = float(o["for_sale"]) / 10 ** base_asset["precision"] * self._get_price(o["sell_price"])
                    rate = self._get_price(o["sell_price"])
                    t = "sell"
                    total = amount / rate
                elif (o["sell_price"]["base"]["asset_id"] == m["quote"] and
                        o["sell_price"]["quote"]["asset_id"] == m["base"]):
                    " buying "
                    amount = float(o["for_sale"]) / 10 ** quote_asset["precision"]
                    rate = 1 / self._get_price(o["sell_price"])
                    t = "buy"
                    total = amount / rate
                else :
                    continue
                r[market].append({"rate" : rate,
                                  "amount" : amount,
                                  "total" : total,
                                  "type" : t,
                                  "orderNumber" : o["id"]})
        if len(markets) == 1 :
            return r[markets[0]]
        else:
            return r

    def returnTradeHistory(self, currencyPair="all", limit=25):
        """ Returns your trade history for a given market, specified by
            the "currencyPair" parameter. You may also specify "all" to
            get the orderbooks of all markets.

            :param str currencyPair: Return results for a particular market only (default: "all")
            :param int limit: Limit the amount of orders (default: 25)


            Output Parameters:

                - `type`: sell or buy
                - `rate`: price for `quote` denoted in `base` ($50c per BTS = 0.5 USD/BTS)
                - `amount`: amount of quote
                - `total`: amount of base at asked price (amount/price)

            Sample output:

            .. code-block:: json

                {'USD_BTS': [{'date': '2016-01-10T17:02:33', 'total':
                0.41650060606060607, 'rate': 0.0030303030303030303,
                'amount': 137.4452, 'type': 'buy'}, {'date':
                '2016-01-10T17:02:33', 'total': 0.9036144578313253,
                'rate': 0.0030120481927710845, 'amount': 300.0, 'type':
                'buy'}, {'date': '2016-01-10T17:02:33', 'total':
                0.29242523928654524, 'rate': 0.0030015759919952414,
                'amount': 97.4239, 'type': 'buy'}], 'GOLD_BTS':
                [{'date': '2016-01-09T15:20:57', 'total':
                4.929095890410958e-07, 'rate': 2.73972602739726e-06,
                'amount': 0.179912, 'type': 'buy'}, {'date':
                '2016-01-09T15:20:42', 'total': 5.454545561157027e-08,
                'rate': 2.7272727805785134e-06, 'amount': 0.02, 'type':
                'buy'}, {'date': '2016-01-07T06:30:21', 'total':
                5.746150000000001e-07, 'rate': 2.5e-06, 'amount':
                0.229846, 'type': 'sell'}]}

            If a single market is chosen, the returning format is
            slightly smaller:

            .. code-block:: json

                [{'date': '2016-01-10T17:02:33', 'type': 'buy', 'rate':
                0.0030303030303030303, 'amount': 137.4452, 'total':
                0.41650060606060607}, {'date': '2016-01-10T17:02:33',
                'type': 'buy', 'rate': 0.0030120481927710845, 'amount':
                300.0, 'total': 0.9036144578313253}, {'date':
                '2016-01-10T17:02:33', 'type': 'buy', 'rate':
                0.0030015759919952414, 'amount': 97.4239,
                'total': 0.29242523928654524}]

            .. note:: A maximum of 25 orders will be returned!

        """
        r = {}
        if currencyPair == "all" :
            markets = list(self.markets.keys())
        else:
            markets = [currencyPair]
        for market in markets :
            m = self.markets[market]
            filled = self.ws.get_fill_order_history(
                m["quote"], m["base"], 2*limit, api="history")
            trades = []
            for f in filled[1::2] :  # every second entry "fills" the order
                data = {}
                data["date"] = f["time"]
                data["rate"] = self._get_price_filled(f, m)
                quote, base = self.ws.get_objects([m["quote"], m["base"]])
                if f["op"]["pays"]["asset_id"] == m["base"] :
                    data["type"]   = "buy"
                    data["amount"] = f["op"]["receives"]["amount"] / 10 ** quote["precision"]
                else :
                    data["type"]   = "sell"
                    data["amount"] = f["op"]["pays"]["amount"] / 10 ** quote["precision"]
                data["total"]  = data["amount"] / data["rate"]
                trades.append(data)

            r.update({market : trades})
        if len(markets) == 1 :
            return r[markets[0]]
        else:
            return r

    def buy(self, currencyPair, rate, amount):
        """ Places a buy order in a given market (buy ``quote``, sell
            ``base`` in market ``quote_base``). Required POST parameters
            are "currencyPair", "rate", and "amount". If successful, the
            method will return the order creating (signed) transaction.

            Example Output:

            .. code-block:: json

                {
                    "expiration": "2016-01-10T18:39:21",
                    "ref_block_prefix": 3510238034,
                    "extensions": [],
                    "ref_block_num": 55601,
                    "signatures": [],
                    "operations": [
                        [
                            1,
                            {
                                "seller": "1.2.22517",
                                "expiration": "2016-01-17T18:38:50",
                                "amount_to_sell": {
                                    "amount": 1000000000,
                                    "asset_id": "1.3.0"
                                },
                                "fee": {
                                    "amount": 1000000,
                                    "asset_id": "1.3.0"
                                },
                                "fill_or_kill": false,
                                "min_to_receive": {
                                    "amount": 100000,
                                    "asset_id": "1.3.121"
                                },
                                "extensions": []
                            }
                        ]
                    ]
                }
        """
        # We buy quote and pay with base
        quote_symbol, base_symbol = currencyPair.split(self.market_separator)
        base = self.rpc.get_asset(base_symbol)
        return self.rpc.sell_asset(self.config.account,
                                   '{:.{prec}f}'.format(amount / rate, prec=base["precision"]),
                                   base_symbol,
                                   amount,
                                   quote_symbol,
                                   7 * 24 * 60 * 60,
                                   False,
                                   False)

    def sell(self, currencyPair, rate, amount):
        """ Places a sell order in a given market (sell ``quote``, buy
            ``base`` in market ``quote_base``). Required POST parameters
            are "currencyPair", "rate", and "amount". If successful, the
            method will return the order creating (signed) transaction.

            Example Output:

            .. code-block:: json

                {
                    "expiration": "2016-01-10T18:39:21",
                    "ref_block_prefix": 3510238034,
                    "extensions": [],
                    "ref_block_num": 55601,
                    "signatures": [],
                    "operations": [
                        [
                            1,
                            {
                                "seller": "1.2.22517",
                                "expiration": "2016-01-17T18:38:52",
                                "amount_to_sell": {
                                    "amount": 100000,
                                    "asset_id": "1.3.121"
                                },
                                "fee": {
                                    "amount": 1000000,
                                    "asset_id": "1.3.0"
                                },
                                "fill_or_kill": false,
                                "min_to_receive": {
                                    "amount": 1000000000,
                                    "asset_id": "1.3.0"
                                },
                                "extensions": []
                            }
                        ]
                    ]
                }


        """
        # We sell quote and pay with base
        quote_symbol, base_symbol = currencyPair.split(self.market_separator)
        quote = self.rpc.get_asset(quote_symbol)
        return self.rpc.sell_asset(self.config.account,
                                   amount,
                                   quote_symbol,
                                   '{:.{prec}f}'.format(amount / rate, prec=quote["precision"]),
                                   base_symbol,
                                   7 * 24 * 60 * 60,
                                   False,
                                   False)

    def cancel(self, currencyPair, orderNumber):
        """ Cancels an order you have placed in a given market. Requires
            only the "orderNumber" (market is included for compatibility
            reasons with Poloniex). An order number takes the form
            ``1.7.xxx``.
        """
        return self.rpc.cancel_order(orderNumber, True)

    def withdraw(self, currency, amount, address):
        """ This Method makes no sense in a decentralized exchange
        """
        raise NotImplementedError
