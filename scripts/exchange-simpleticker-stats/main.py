from grapheneexchange import GrapheneExchange
import math


class Config():
    wallet_host           = "localhost"
    wallet_port           = 8092
    wallet_user           = ""
    wallet_password       = ""
    witness_url           = "ws://10.0.0.16:8090/"
    witness_user          = ""
    witness_password      = ""

    watch_markets         = ["USD_BTS", "CNY_BTS", "GOLD_BTS", "SILVER_BTS", "EUR_BTS"]
    market_separator      = "_"
    account               = "xeroc"

if __name__ == '__main__':
    dex   = GrapheneExchange(Config, safe_mode=True)
    ticker = dex.returnTicker()
    for a in ticker:
        premium = math.fabs((ticker[a]["last"] / ticker[a]["settlement_price"] - 1) * 100)
        premium_bid = ((ticker[a]["settlement_price"] / ticker[a]["highestBid"] - 1) * 100)
        premium_ask = ((ticker[a]["settlement_price"] / ticker[a]["lowestAsk"] - 1) * 100)
        premium = math.fabs((ticker[a]["settlement_price"] / ticker[a]["last"] - 1) * 100)
        price_mid = (ticker[a]["highestBid"] + ticker[a]["lowestAsk"]) / 2.0
        spread = math.fabs(ticker[a]["highestBid"] - ticker[a]["lowestAsk"]) / price_mid * 100
        cer_premium = (ticker[a]["core_exchange_rate"] / ticker[a]["settlement_price"] - 1) * 100

        print("\n%s" % a)
        print("=" * len(a))
        print(" - Last Trade Premium: %+7.3f%%" % premium)
        print(" - Ask Order Premium:  %+7.3f%%" % premium_bid)
        print(" - Bid Order Premium:  %+7.3f%%" % premium_ask)
        print(" - Spread:             %+7.3f%%" % spread)
        print(" - CER premium:        %+7.3f%%" % cer_premium)
