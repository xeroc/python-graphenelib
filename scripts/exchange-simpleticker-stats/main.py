from grapheneexchange import GrapheneExchange
import math


class Config():
    wallet_host           = "localhost"
    wallet_port           = 8092
    wallet_user           = ""
    wallet_password       = ""
    witness_url           = "ws://10.0.0.16:8090/"
    # witness_url           = "ws://testnet.bitshares.eu/ws"
    witness_user          = ""
    witness_password      = ""

    watch_markets         = ["USD_BTS", "CNY_BTS", "GOLD_BTS", "SILVER_BTS", "EUR_BTS", "BTC_BTS"]
    # watch_markets         = ["PEG.RANDOM_TEST"]
    market_separator      = "_"
    account               = "xeroc"

if __name__ == '__main__':
    dex   = GrapheneExchange(Config, safe_mode=True)
    ticker = dex.returnTicker()
    for a in ticker:
        quote, base = a.split(Config.market_separator)
        premium = math.fabs((ticker[a]["last"] / ticker[a]["settlement_price"] - 1) * 100)
        premium_bid = ((ticker[a]["highestBid"] / ticker[a]["settlement_price"] - 1) * 100)
        premium_ask = ((ticker[a]["lowestAsk"] / ticker[a]["settlement_price"] - 1) * 100)
        premium = math.fabs((ticker[a]["last"] / ticker[a]["settlement_price"] - 1) * 100)
        price_mid = (ticker[a]["highestBid"] + ticker[a]["lowestAsk"]) / 2.0
        spread = math.fabs(ticker[a]["highestBid"] - ticker[a]["lowestAsk"])
        cer_premium = (ticker[a]["settlement_price"] / ticker[a]["core_exchange_rate"] - 1) * 100

        print("\n%s" % a)
        print("=" * len(a))
        print(" - Last Trade Premium: %+9.3f%% (%.3f)" % (premium, ticker[a]["last"]))
        print(" - Ask Order Premium:  %+9.3f%%" % premium_bid)
        print(" - Bid Order Premium:  %+9.3f%%" % premium_ask)
        print(" - Spread:              %9.3f %s/%s" % (spread, base, quote))
        print(" - CER premium:        %+9.3f%%" % cer_premium)
