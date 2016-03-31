from grapheneexchange import GrapheneExchange
from pprint import pprint


class config():
    wallet_host = "localhost"
    wallet_port = 8092
    witness_url = "wss://bitshares.openledger.info/ws"

    watch_markets = ["BTS:USD"]  # market: quote:base .. trade:quote .. price: base/quote
    market_separator = ":"

    account = "live-coding"

dex = GrapheneExchange(config, safe_mode=False, propose_only=False)

pprint(dex.returnTicker())

# pprint(dex.returnBalances())
# pprint(dex.returnTradeHistory(limit=5))

# lowestAsk = dex.returnTicker()["USD:BTS"]["lowestAsk"]
# pprint(dex.buy("USD:BTS", lowestAsk*0.99, 1))
# pprint(dex.sell("USD:BTS", lowestAsk*1.10, 1))

## FIXME
## pprint(dex.returnOpenOrders())

# pprint(dex.cancel("1.7.189477"))

#pprint(dex.borrow(10, "USD", 3.0))
#pprint(dex.adjust_debt(+1, "USD", 2.5))
#pprint(dex.list_debt_positions())
#pprint(dex.close_debt_position("USD"))

# pprint(dex.get_lowest_ask())

# pprint(dex.get_my_bids_out_of_range("USD:BTS", 180, limit=25))

# pprint(dex.propose_all())
