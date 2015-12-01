import requests
import json
import sys
import re

_request_headers = {'content-type': 'application/json',
                 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}

core_symbol = "BTS"

_yahoo_base  = ["USD","EUR","CNY","JPY","HKD"]
_yahoo_quote = ["XAG", "XAU", "TRY", "SGD", "HKD", "NZD", "CNY",
             "MXN", "CAD", "CHF", "AUD", "GBP", "JPY", "EUR", "USD", "KRW"] # , "RUB", "SEK"
_yahoo_indices = {
#                    "399106.SZ" : core_symbol,  #"CNY",  # SHENZHEN
#                    "^HSI"      : core_symbol,  #"HKD",  # HANGSENG
#                    "^IXIC"     : core_symbol,  #"USD",  # NASDAQC
#                    "^N225"     : core_symbol   #"JPY"   # NIKKEI
             }
_bts_yahoo_map = {
  "XAU"       : "GOLD",
  "XAG"       : "SILVER",
  "399106.SZ" : "SHENZHEN",
  "000001.SS" : "SHANGHAI",
  "^HSI"      : "HANGSENG",
  "^IXIC"     : "NASDAQC",
  "^N225"     : "NIKKEI"
}

class FeedSource() :
    def __init__(self, trust=1.0, enable=True, allowFailure=False):
        self.trust        = trust
        self.enabled      = enable
        self.allowFailure = allowFailure
        
        ## Why fail if the trust is 0
        if self.trust == 0.0 :
            self.allowFailure = True

class BitcoinIndonesia(FeedSource) :
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)
  
    def fetch(self):
      feed = {}
      feed["BTC"]  = {}
      availableAssets = [ core_symbol ]
      for coin in availableAssets :
       try :
        url="https://vip.bitcoin.co.id/api/%s_btc/ticker" % coin.lower()
        response = requests.get(url=url, headers=_request_headers, timeout=10 )
        result = response.json()["ticker"]
        feed["BTC"][ coin ]  = { "price"  : float(result["last"]),
                                 "volume" : float(result["vol_"+coin.lower()])*self.trust }
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
      bts_markets = {
                      "CNY":123,
                      "USD":55,
                      "BTC":50,
                      "EUR":54,
                    }
      for market in bts_markets : 
       pair_id = bts_markets[market]
       feed[market] = {}
       try :
        url="https://www.ccedk.com/api/v1/stats/marketdepthfull?pair_id=%d" % pair_id
        response = requests.get(url=url, headers=_request_headers, timeout=10 )
        result = response.json()["response"]["entity"]
        feed[market][core_symbol]  = { "price"  : float(result["last_price"]),
                                       "volume" : float(result["vol"])*self.trust}
       except Exception as e:
        print("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
        if not self.allowFailure:
         sys.exit("\nExiting due to exchange importance!")
        return
      return feed

class Yunbi(FeedSource) :
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)

    def fetch(self):
      feed  = {}
      feed["BTC"]  = {}
      feed["CNY"]  = {}
      try :
       url="https://yunbi.com/api/v2/tickers.json"
       response = requests.get(url=url, headers=_request_headers, timeout=10)
       result = response.json()
      except Exception as e:
       print("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
       if not self.allowFailure:
        sys.exit("\nExiting due to exchange importance")
       return
      availableAssets = [ core_symbol ]
      for coin in availableAssets :
       feed["BTC"][ coin ] = { "price"  : (float(result[coin.lower()+"btc"]["ticker"]["last"])),
                               "volume" : (float(result[coin.lower()+"btc"]["ticker"]["vol"])*self.trust) }
      availableAssets = [ core_symbol, "BTC" ]
      for coin in availableAssets :
       feed["CNY"][ coin ] = { "price"  : (float(result[coin.lower()+"cny"]["ticker"]["last"])),
                               "volume" : (float(result[coin.lower()+"cny"]["ticker"]["vol"])*self.trust) }
      return feed 

class Btc38(FeedSource) :
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)

    def fetch(self):
      feed  = {}
      feed["BTC"]  = {}
      feed["CNY"]  = {}
      url="http://api.btc38.com/v1/ticker.php"
      availableAssets = [ core_symbol ]
      try :
       params = { 'c': 'bts', 'mk_type': 'btc' }
       response = requests.get(url=url, params=params, headers=_request_headers, timeout=10 )
       result = response.json()
       for coin in availableAssets :
        feed["BTC"][ coin ] = { "price"  : (float(result[coin.lower()]["ticker"]["last"])),
                                "volume" : (float(result[coin.lower()]["ticker"]["vol"]/result[coin.lower()]["ticker"]["last"])*self.trust) }

       availableAssets = [ core_symbol, "BTC" ]
      except Exception as e:
       print("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
       if not self.allowFailure:
        sys.exit("\nExiting due to exchange importance!")
       return
      try :
       params = { 'c': 'all', 'mk_type': 'cny' }
       response = requests.get(url=url, params=params, headers=_request_headers, timeout=10 )
       result = response.json()
       for coin in availableAssets:
        feed["CNY"][ coin ] = { "price"  : (float(result[coin.lower()]["ticker"]["last"])),
                                "volume" : (float(result[coin.lower()]["ticker"]["vol"])*float(result[coin.lower()]["ticker"]["last"])*self.trust) }
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
      volume = {}
      try :
       url="http://data.bter.com/api/1/tickers"
       response = requests.get(url=url, headers=_request_headers, timeout=10 )
       result = response.json()
      except Exception as e:
       print("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
       if not self.allowFailure:
        sys.exit("\nExiting due to exchange importance")
       return
      availableAssets = [ "BTC", core_symbol ]
      for market in ["BTC", "CNY", "USD"] :
       feed[market]  = {}
       for coin in availableAssets :
        if coin == market : continue
        feed[market][coin] = { "price"  : (float(result[coin.lower()+"_"+market.lower()]["last"])),
                               "volume" : (float(result[coin.lower()+"_"+market.lower()]["vol_"+market.lower()])*self.trust) }
      return feed

class Poloniex(FeedSource) :
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)

    def fetch(self):
      feed  = {}
      feed["BTC"]  = {}
      try :
       url="https://poloniex.com/public?command=returnTicker"
       response = requests.get(url=url, headers=_request_headers, timeout=10 )
       result = response.json()
       availableAssets = [ core_symbol ]
      except Exception as e:
       print("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
       if not self.allowFailure:
        sys.exit("\nExiting due to exchange importance!")
       return
      for coin in availableAssets :
       feed["BTC"][ coin ] = { "price"  : (float(result["BTC_"+coin]["last"])),
                               "volume" : (float(result["BTC_"+coin]["quoteVolume"])*self.trust) }
      return feed

class Bittrex(FeedSource) :
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)

    def fetch(self):
      feed  = {}
      feed["BTC"]  = {}
      availableAssets = [ "BTS" ]
      try:
       url="https://bittrex.com/api/v1.1/public/getmarketsummaries"
       response = requests.get(url=url, headers=_request_headers, timeout=10 )
       result = response.json()["result"]
      except Exception as e:
       print("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
       if not self.allowFailure:
        sys.exit("\nExiting due to exchange importance!")
       return
      for coin in result :
       if( coin[ "MarketName" ] in ["BTC-"+a for a in availableAssets] ) :
        mObj    = re.match( 'BTC-(.*)', coin[ "MarketName" ] )
        feed["BTC"][ mObj.group(1) ] = { "price" : (float(coin["Last"])),
                                         "volume" : (float(coin["Volume"])*self.trust) }
      return feed 

class Yahoo(FeedSource) :
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)

    def bts_yahoo_map(self,asset) :
     if asset in _bts_yahoo_map:
      return _bts_yahoo_map[asset]
     else :
      return asset

    def fetch(self):
      feed = {}
      feed[core_symbol] = {}
      try :
          # Currencies and commodities
          for base in _yahoo_base :
           feed[base] = {}
           yahooAssets = ",".join([a+base+"=X" for a in _yahoo_quote])
           url="http://download.finance.yahoo.com/d/quotes.csv"
           params = {'s':yahooAssets,'f':'l1','e':'.csv'}
           response = requests.get(url=url, headers=_request_headers, timeout=10 ,params=params)
           yahooprices =  response.text.replace('\r','').split( '\n' )
           for i,a in enumerate(_yahoo_quote) :
            if float(yahooprices[i]) > 0 :
             feed[base][ self.bts_yahoo_map(a) ] = {"price"  : (float(yahooprices[i])),
                                                    "volume" : 1.0, }
          # # indices
          # yahooAssets = ",".join(_yahoo_indices.keys())
          # url="http://download.finance.yahoo.com/d/quotes.csv"
          # params = {'s':yahooAssets,'f':'l1','e':'.csv'}
          # response = requests.get(url=url, headers=_request_headers, timeout=10 ,params=params)
          # yahooprices =  response.text.replace('\r','').split( '\n' )
          # for i,a in enumerate(_yahoo_indices) :
          #  if float(yahooprices[i]) > 0 :
          #   feed[ core_symbol ][ self.bts_yahoo_map(a) ] = { "price"  : (1/float(yahooprices[i])),
          #                                                    "volume" : 1.0, }
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
      url="https://api.bitcoinaverage.com/ticker/"
      availableAssets = [ "USD", "EUR", "CNY" ]
      for coin in availableAssets :
       feed[coin] = {}
       response = requests.get(url=url+coin, headers=_request_headers, timeout=10)
       result = response.json()
       feed[coin][ "BTC" ] = { "price"  : (float(result["last"])),
                               "volume" : (float(result["total_vol"])) }
      return feed

class BtcChina(FeedSource) :
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)

    def fetch(self):
      feed  = {}
      markets = ["CNY"]
      availableAssets = [ "BTC" ]
      try :
          for market in markets :
              feed[market] = {}
              for coin in availableAssets :
                  url="https://data.btcchina.com/data/ticker?market=%s%s" % (coin.lower(), market.lower())
                  response = requests.get(url=url, headers=_request_headers, timeout=10 )
                  result = response.json()
                  feed[market][coin] = { "price"  : (float(result["ticker"]["last"])),
                                         "volume" : (float(result["ticker"]["vol"])*self.trust) }
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
      markets = ["CNY"]
      availableAssets = [ "BTC" ]
      try :
          for market in markets :
              feed[market] = {}
              for coin in availableAssets :
                  url="http://api.huobi.com/staticmarket/ticker_%s_json.js" % (coin.lower())
                  response = requests.get(url=url, headers=_request_headers, timeout=10 )
                  result = response.json()
                  feed[market][coin] = { "price"  : (float(result["ticker"]["last"])),
                                         "volume" : (float(result["ticker"]["vol"])*self.trust) }
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
      markets = ["USD","CNY"]
      availableAssets = [ "BTC" ]
      try :
          for market in markets :
              feed[market] = {}
              for coin in availableAssets :
                  if market == "USD" :
                      url="https://www.okcoin.com/api/v1/ticker.do?symbol=%s_%s" % (coin.lower(), market.lower())
                  elif market == "CNY" : 
                      url="https://www.okcoin.cn/api/ticker.do?symbol=%s_%s" % (coin.lower(), market.lower())
                  else : 
                    sys.exit("\n%s does not know market type %s" % (type(self).__name__, market))
                  response = requests.get(url=url, headers=_request_headers, timeout=10 )
                  result = response.json()
                  feed[market][coin] = { "price"  : (float(result["ticker"]["last"])),
                                         "volume" : (float(result["ticker"]["vol"])*self.trust) }
      except Exception as e:
       print("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
       if not self.allowFailure:
        sys.exit("\nExiting due to exchange importance!")
       return
      return feed
