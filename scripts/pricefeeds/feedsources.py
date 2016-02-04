import requests
import sys
import config

_request_headers = {'content-type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}

_yahoo_base  = ["USD", "EUR", "CNY", "JPY", "HKD"]
_yahoo_quote = ["XAG", "XAU", "TRY", "SGD", "HKD", "NZD", "CNY",
                "MXN", "CAD", "CHF", "AUD", "GBP", "JPY", "EUR", "USD", "KRW"]  # "RUB", "SEK"
_yahoo_indices = {}
# "399106.SZ" : config.core_symbol,  #"CNY",  # SHENZHEN
# "^HSI"      : config.core_symbol,  #"HKD",  # HANGSENG
# "^IXIC"     : config.core_symbol,  #"USD",  # NASDAQC
# "^N225"     : config.core_symbol   #"JPY"   # NIKKEI
_bts_yahoo_map = {"XAU"       : "GOLD",
                  "XAG"       : "SILVER",
                  "399106.SZ" : "SHENZHEN",
                  "000001.SS" : "SHANGHAI",
                  "^HSI"      : "HANGSENG",
                  "^IXIC"     : "NASDAQC",
                  "^N225"     : "NIKKEI"
                  }


class FeedSource() :
    def __init__(self, scaleVolumeBy=1.0,
                 enable=True,
                 allowFailure=False,
                 timeout=20,
                 quotes=[],
                 bases=[]):
        self.scaleVolumeBy = scaleVolumeBy
        self.enabled       = enable
        self.allowFailure  = allowFailure
        self.timeout       = timeout
        self.bases         = bases
        self.quotes        = quotes
        # Why fail if the scaleVolumeBy is 0
        if self.scaleVolumeBy == 0.0 :
            self.allowFailure = True


class BitcoinIndonesia(FeedSource) :
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)

    def fetch(self):
        feed = {}
        try :
            for base in self.bases:
                feed[base] = {}
                for quote in self.quotes :
                    url = "https://vip.bitcoin.co.id/api/%s_%s/ticker" % (quote.lower(), base.lower())
                    response = requests.get(url=url, headers=_request_headers, timeout=self.timeout)
                    result = response.json()["ticker"]
                    feed[base][quote]  = {"price"  : float(result["last"]),
                                          "volume" : float(result["vol_" + quote.lower()]) * self.scaleVolumeBy}
                    feed[base]["response"] = response.json()
        except Exception as e:
            print("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
            if not self.allowFailure:
                sys.exit("\nExiting due to exchange importance!")
            return
        return feed


class Ccedk(FeedSource) :
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)

    def fetch(self):
        feed  = {}
        bts_markets = {"CNY" : 123,
                       "USD" : 55,
                       "BTC" : 50,
                       "EUR" : 54}
        try :
            for base in self.bases :
                quote = self.quotes[0]
                if base not in bts_markets or quote != config.core_symbol:
                    print("Base %s has its base not implemented here!" % base)
                    return
                pair_id = bts_markets[base]
                feed[base] = {}
                url = "https://www.ccedk.com/api/v1/stats/marketdepthfull?pair_id=%d" % pair_id
                response = requests.get(url=url, headers=_request_headers, timeout=self.timeout)
                result = response.json()
                feed[base]["response"] = result
                if ("response" in result and result["response"] and "entity" in result["response"]):
                    if ("last_price" in result["response"]["entity"] and
                            "vol" in result["response"]["entity"]):
                        feed[base][quote]  = {"price"  : float(result["response"]["entity"]["last_price"]),
                                              "volume" : float(result["response"]["entity"]["vol"]) * self.scaleVolumeBy}
        except Exception as e:
            print("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
            import traceback
            traceback.print_exc()
            if not self.allowFailure:
                sys.exit("\nExiting due to exchange importance!")
            return
        return feed


class Yunbi(FeedSource) :
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)

    def fetch(self):
        feed  = {}
        try :
            url = "https://yunbi.com/api/v2/tickers.json"
            response = requests.get(url=url, headers=_request_headers, timeout=self.timeout)
            result = response.json()
            feed["response"] = result
            for base in self.bases :
                feed[base] = {}
                for quote in self.quotes :
                    if quote == base :
                        continue
                    marketName = quote.lower() + base.lower()
                    if marketName in result :
                        feed[base][quote] = {"price"  : (float(result[marketName]["ticker"]["last"])),
                                             "volume" : (float(result[marketName]["ticker"]["vol"]) * self.scaleVolumeBy)}
        except Exception as e:
            print("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
            if not self.allowFailure:
                sys.exit("\nExiting due to exchange importance!")
            return
        return feed


class Btc38(FeedSource) :
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)

    def fetch(self):
        feed  = {}
        url = "http://api.btc38.com/v1/ticker.php"
        try :
            for base in self.bases :
                feed[base] = {}
                for quote in self.quotes :
                    if base == quote :
                        continue
                    params = {'c': quote.lower(), 'mk_type': base.lower()}
                    response = requests.get(url=url, params=params, headers=_request_headers, timeout=self.timeout)
                    result = response.json()
                    feed["response"] = result
                    if "ticker" in result and \
                       "last" in result["ticker"] and \
                       "vol" in result["ticker"] :
                        feed[base][quote] = {"price"  : (float(result["ticker"]["last"])),
                                             "volume" : (float(result["ticker"]["vol"]) * self.scaleVolumeBy)}
                    else :
                        print("\nFetched data from {0} is empty!".format(type(self).__name__))
                        continue
        except Exception as e:
            print("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
            if not self.allowFailure:
                sys.exit("\nExiting due to exchange importance!")
            return
        return feed


class Bter(FeedSource) :
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)

    def fetch(self):
        feed  = {}
        try :
            url = "http://data.bter.com/api/1/tickers"
            response = requests.get(url=url, headers=_request_headers, timeout=self.timeout)
            result = response.json()
            feed["response"] = result
            for base in self.bases :
                feed[base]  = {}
                for quote in self.quotes :
                    if quote == base :
                        continue
                    if quote.lower() + "_" + base.lower() in result :
                        feed[base][quote] = {"price"  : (float(result[quote.lower() + "_" + base.lower()]["last"])),
                                             "volume" : (float(result[quote.lower() + "_" + base.lower()]["vol_" + base.lower()]) * self.scaleVolumeBy)}
        except Exception as e:
            print("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
            if not self.allowFailure:
                sys.exit("\nExiting due to exchange importance!")
            return
        return feed


class Poloniex(FeedSource) :
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)

    def fetch(self):
        feed  = {}
        try :
            url = "https://poloniex.com/public?command=returnTicker"
            response = requests.get(url=url, headers=_request_headers, timeout=self.timeout)
            result = response.json()
            feed["response"] = result
            for base in self.bases :
                feed[base]  = {}
                for quote in self.quotes :
                    if quote == base :
                        continue
                    marketName = base + "_" + quote
                    if marketName in result :
                        feed[base][quote] = {"price"  : (float(result[marketName]["last"])),
                                             "volume" : (float(result[marketName]["quoteVolume"]) * self.scaleVolumeBy)}
        except Exception as e:
            print("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
            if not self.allowFailure:
                sys.exit("\nExiting due to exchange importance!")
            return
        return feed


class Bittrex(FeedSource) :
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)

    def fetch(self):
        feed  = {}
        try :
            url = "https://bittrex.com/api/v1.1/public/getmarketsummaries"
            response = requests.get(url=url, headers=_request_headers, timeout=self.timeout)
            result = response.json()["result"]
            feed["response"] = response.json()
            for base in self.bases:
                feed[base] = {}
                for thisMarket in result :
                    for quote in self.quotes :
                        if quote == base :
                            continue
                        if thisMarket["MarketName"] == base + "-" + quote :
                            feed[base][quote] = {"price" : (float(thisMarket["Last"])),
                                                 "volume" : (float(thisMarket["Volume"]) * self.scaleVolumeBy)}
        except Exception as e:
            print("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
            if not self.allowFailure:
                sys.exit("\nExiting due to exchange importance!")
            return
        return feed


class Yahoo(FeedSource) :
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)

    def bts_yahoo_map(self, asset) :
        if asset in _bts_yahoo_map:
            return _bts_yahoo_map[asset]
        else :
            return asset

    def fetch(self):
        feed = {}
        feed[config.core_symbol] = {}
        try :
            # Currencies and commodities
            for base in _yahoo_base :
                feed[base] = {}
                yahooAssets = ",".join([a + base + "=X" for a in _yahoo_quote])
                url = "http://download.finance.yahoo.com/d/quotes.csv"
                params = {'s' : yahooAssets, 'f' : 'l1', 'e' : '.csv'}
                response = requests.get(url=url, headers=_request_headers, timeout=self.timeout, params=params)
                yahooprices = response.text.replace('\r', '').split('\n')
                for i, a in enumerate(_yahoo_quote) :
                    if float(yahooprices[i]) > 0 :
                        feed[base][self.bts_yahoo_map(a)] = {"price"  : (float(yahooprices[i])),
                                                             "volume" : 1.0}
#                # indices
#                yahooAssets = ",".join(_yahoo_indices.keys())
#                url="http://download.finance.yahoo.com/d/quotes.csv"
#                params = {'s':yahooAssets,'f':'l1','e':'.csv'}
#                response = requests.get(url=url, headers=_request_headers, timeout=self.timeout ,params=params)
#                yahooprices =  response.text.replace('\r','').split( '\n' )
#                for i,a in enumerate(_yahoo_indices) :
#                    if float(yahooprices[i]) > 0 :
#                        feed[ config.core_symbol ][ self.bts_yahoo_map(a) ] = { "price"  : (1/float(yahooprices[i])),
#                                                                         "volume" : 1.0, }
        except Exception as e:
            print("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
            if not self.allowFailure:
                sys.exit("\nExiting due to exchange importance!")
            return
        return feed


class BitcoinAverage(FeedSource) :
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)

    def fetch(self):
        feed = {}
        url = "https://api.bitcoinaverage.com/ticker/"
        try :
            for base in self.bases :
                feed[base] = {}
                for quote in self.quotes :
                    if quote == base:
                        continue
                    response = requests.get(url=url + base, headers=_request_headers, timeout=self.timeout)
                    result = response.json()
                    feed[base]["response"] = result
                    feed[base][quote] = {"price"  : (float(result["last"])),
                                         "volume" : (float(result["total_vol"]))}
        except Exception as e:
            print("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
            if not self.allowFailure:
                sys.exit("\nExiting due to exchange importance!")
            return
        return feed


class BtcChina(FeedSource) :
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)

    def fetch(self):
        feed  = {}
        try :
            for base in self.bases :
                feed[base] = {}
                for quote in self.quotes :
                    url = "https://data.btcchina.com/data/ticker?base=%s%s" % (quote.lower(), base.lower())
                    response = requests.get(url=url, headers=_request_headers, timeout=self.timeout)
                    result = response.json()
                    feed[base]["response"] = result
                    feed[base][quote] = {"price"  : (float(result["ticker"]["last"])),
                                         "volume" : (float(result["ticker"]["vol"]) * self.scaleVolumeBy)}
        except Exception as e:
            print("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
            if not self.allowFailure:
                sys.exit("\nExiting due to exchange importance!")
            return
        return feed


class Huobi(FeedSource) :
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)

    def fetch(self):
        feed  = {}
        try :
            for base in self.bases :
                feed[base] = {}
                for quote in self.quotes :
                    url = "http://api.huobi.com/staticmarket/ticker_%s_json.js" % (quote.lower())
                    response = requests.get(url=url, headers=_request_headers, timeout=self.timeout)
                    result = response.json()
                    feed[base]["response"] = result
                    feed[base][quote] = {"price"  : (float(result["ticker"]["last"])),
                                         "volume" : (float(result["ticker"]["vol"]) * self.scaleVolumeBy)}
        except Exception as e:
            print("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
            if not self.allowFailure:
                sys.exit("\nExiting due to exchange importance!")
            return
        return feed


class Okcoin(FeedSource) :
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)

    def fetch(self):
        feed  = {}
        try :
            for base in self.bases :
                feed[base] = {}
                for quote in self.quotes :
                    if base == "USD" :
                        url = "https://www.okcoin.com/api/v1/ticker.do?symbol=%s_%s" % (quote.lower(), base.lower())
                    elif base == "CNY" :
                        url = "https://www.okcoin.cn/api/ticker.do?symbol=%s_%s" % (quote.lower(), base.lower())
                    else :
                        sys.exit("\n%s does not know base type %s" % (type(self).__name__, base))
                    response = requests.get(url=url, headers=_request_headers, timeout=self.timeout)
                    result = response.json()
                    feed[base]["response"] = result
                    feed[base][quote] = {"price"  : (float(result["ticker"]["last"])),
                                         "volume" : (float(result["ticker"]["vol"]) * self.scaleVolumeBy)}
        except Exception as e:
            print("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
            if not self.allowFailure:
                sys.exit("\nExiting due to exchange importance!")
            return
        return feed
