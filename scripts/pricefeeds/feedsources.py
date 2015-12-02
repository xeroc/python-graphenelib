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
    def __init__(self, scaleVolumeBy=1.0, enable=True, allowFailure=False):
        self.scaleVolumeBy = scaleVolumeBy
        self.enabled       = enable
        self.allowFailure  = allowFailure
        
        ## Why fail if the scaleVolumeBy is 0
        if self.scaleVolumeBy == 0.0 :
            self.allowFailure = True

class BitcoinIndonesia(FeedSource) :
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)
  
    def fetch(self):
      feed = {}
      markets         = [ "BTC" ]
      availableAssets = [ core_symbol ]
      for market in markets :
       feed[market] = {}
       for coin in availableAssets :
        try :
         url="https://vip.bitcoin.co.id/api/%s_%s/ticker" % (coin.lower(),market.lower())
         response = requests.get(url=url, headers=_request_headers, timeout=10 )
         result = response.json()["ticker"]
         feed[market][coin]  = { "price"  : float(result["last"]),
                                 "volume" : float(result["vol_"+coin.lower()])*self.scaleVolumeBy }
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
                      "CNY" : 123,
                      "USD" : 55,
                      "BTC" : 50,
                      "EUR" : 54,
                    }
      for market in bts_markets : 
       pair_id = bts_markets[market]
       feed[market] = {}
       try :
        url="https://www.ccedk.com/api/v1/stats/marketdepthfull?pair_id=%d" % pair_id
        response = requests.get(url=url, headers=_request_headers, timeout=10 )
        result = response.json()["response"]["entity"]
        feed[market][core_symbol]  = { "price"  : float(result["last_price"]),
                                       "volume" : float(result["vol"])*self.scaleVolumeBy}
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
      markets         = ["BTC","CNY"]
      availableAssets = [ core_symbol, "BTC" ]
      try :
       url="https://yunbi.com/api/v2/tickers.json"
       response = requests.get(url=url, headers=_request_headers, timeout=10)
       result = response.json()
       for market in markets : 
        feed[market] = {}
        for coin in availableAssets :
         if coin == market : continue
         marketName = coin.lower()+market.lower()
         if marketName in result : 
          feed[market][coin] = { "price"  : (float(result[marketName]["ticker"]["last"])),
                                 "volume" : (float(result[marketName]["ticker"]["vol"])*self.scaleVolumeBy) }
      except Exception as e:
       print("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
       if not self.allowFailure:
        sys.exit("\nExiting due to exchange importance")
       return
      return feed 

class Btc38(FeedSource) :
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)

    def fetch(self):
      feed  = {}
      markets         = ["BTC", "CNY"]
      availableAssets = [ core_symbol, "BTC" ]
      url="http://api.btc38.com/v1/ticker.php"
      try :
       for market in markets : 
        feed[market] = {}
        for coin in availableAssets :
         if market == coin : continue
         params = { 'c': coin.lower(), 'mk_type': market.lower() }
         response = requests.get(url=url, params=params, headers=_request_headers, timeout=10 )
         result = response.json()
         if coin.lower() in result :
          feed[market][coin] = {  "price"  : (float(result[coin.lower()]["ticker"]["last"])),
                                  "volume" : (float(result[coin.lower()]["ticker"]["vol"]/result[coin.lower()]["ticker"]["last"])*self.scaleVolumeBy) }
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
      markets         = ["BTC", "CNY", "USD"]
      availableAssets = [ "BTC", core_symbol ]
      try :
       url="http://data.bter.com/api/1/tickers"
       response = requests.get(url=url, headers=_request_headers, timeout=10 )
       result = response.json()
       for market in markets :
        feed[market]  = {}
        for coin in availableAssets :
         if coin == market : continue
         if coin.lower()+"_"+market.lower() in result : 
          feed[market][coin] = { "price"  : (float(result[coin.lower()+"_"+market.lower()]["last"])),
                                 "volume" : (float(result[coin.lower()+"_"+market.lower()]["vol_"+market.lower()])*self.scaleVolumeBy) }
      except Exception as e:
       print("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
       if not self.allowFailure:
        sys.exit("\nExiting due to exchange importance")
       return
      return feed

class Poloniex(FeedSource) :
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)

    def fetch(self):
      feed  = {}
      markets         = ["BTC"]
      availableAssets = [ core_symbol ]
      try :
       url="https://poloniex.com/public?command=returnTicker"
       response = requests.get(url=url, headers=_request_headers, timeout=10 )
       result = response.json()
       for market in markets :
        feed[market]  = {}
        for coin in availableAssets :
         if coin == market : continue
         marketName = market+"_"+coin
         if marketName in result : 
          feed[market][coin] = { "price"  : (float(result[marketName]["last"])),
                                 "volume" : (float(result[marketName]["quoteVolume"])*self.scaleVolumeBy) }
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
      markets = ["BTC"]
      availableAssets = [ "BTS" ]
      try:
       url="https://bittrex.com/api/v1.1/public/getmarketsummaries"
       response = requests.get(url=url, headers=_request_headers, timeout=10 )
       result = response.json()["result"]
       for market in markets : 
        feed[market] = {}
        for thisMarket in result :
         for coin in availableAssets :
          if coin==market : continue
          if thisMarket[ "MarketName" ] == market+"-"+coin : 
           feed[market][coin] = { "price" : (float(thisMarket["Last"])),
                                  "volume" : (float(thisMarket["Volume"])*self.scaleVolumeBy) }
      except Exception as e:
       print("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
       if not self.allowFailure:
        sys.exit("\nExiting due to exchange importance!")
       return
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
      markets = [ "USD", "EUR", "CNY" ]
      availableAssets = ["BTC"]
      url="https://api.bitcoinaverage.com/ticker/"
      try :
       for market in markets :
        feed[market] = {}
        for coin in availableAssets :
         if coin == market: continue
         response = requests.get(url=url+market, headers=_request_headers, timeout=10)
         result = response.json()
         feed[market][coin] = { "price"  : (float(result["last"])),
                                "volume" : (float(result["total_vol"])) }
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
                                         "volume" : (float(result["ticker"]["vol"])*self.scaleVolumeBy) }
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
                                         "volume" : (float(result["ticker"]["vol"])*self.scaleVolumeBy) }
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
                                         "volume" : (float(result["ticker"]["vol"])*self.scaleVolumeBy) }
      except Exception as e:
       print("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
       if not self.allowFailure:
        sys.exit("\nExiting due to exchange importance!")
       return
      return feed
