import requests

class Alpaca:
   def __init__(self, key, secret):
      self.session = requests.Session()
      self.session.headers = {
         "accept": "application/json",
         "APCA-API-KEY-ID": key,
         "APCA-API-SECRET-KEY": secret,
         "Connection": "keep-alive"
      }

      #self.robinhood = robinhood

      self.trades = {"brokerage": {}}
      #self.trades["brokerage"]["daytrades"] = requests.get("https://api.alpaca.markets/v2/account", headers=headers).json()["daytrade_count"]

   def get_timestamp(self, h=None, m=None, specific_date=None):
      current_time = datetime.now(pytz.timezone("EST"))
      return current_time.strftime('%Y-%m-%dT%H:%M:%S-05:00')

   def get_prev_mins(self, m):
      current_time = datetime.now(pytz.timezone("EST"))
      time_ago = current_time - timedelta(minutes=m)
      return time_ago.strftime('%Y-%m-%dT%H:%M:%S-05:00')


   def get_bars(self, ticker, _from, to, limit, sort, timeframe, result_queue=None ):
   '''
   _from	- 2024-01-03T00:00:00Z
   _to		- 2024-02-03T00:00:00Z
   limit	- 1 to 10000 (Defaults to 1000)
   sort		- asc or desc
   timeframe	- [1-59]Min or [1-59]T, e.g. 5Min or 5T creates 5-minute aggregations
		  [1-23]Hour or [1-23]H, e.g. 12Hour or 12H creates 12-hour aggregations
		  1Day or 1D creates 1-day aggregations
		  1Week or 1W creates 1-week aggregations
		  [1,2,3,4,6,12]Month or [1,2,3,4,6,12]M, e.g. 3Month or 3M

   {
     "bars": {
       "AAPL": [
         {
           "c": 185.31,
           "h": 185.31,
           "l": 185.31,
           "n": 28,
           "o": 185.31,
           "t": "2024-01-03T00:00:00Z",
           "v": 1045,
           "vw": 185.31
         },
         {
           "c": 185.29,
           "h": 185.29,
           "l": 185.29,
           "n": 36,
           "o": 185.29,
           "t": "2024-01-03T00:01:00Z",
           "v": 283,
           "vw": 185.29
         }
       ]
     },
     "next_page_token": "QUFQTHxNfDE3MDQyNDAwNjAwMDAwMDAwMDA="
   }
   '''

      #url = "https://data.alpaca.markets/v2/stocks/bars?symbols=" + ticker + "&start=" + f + "&end=" + t + "&limit=" + l + "&feed=sip&sort=" + s + "&timeframe=" + tf
      #if get_otc_status(ticker) == "otc":
      #   url = "https://data.alpaca.markets/v2/stocks/" + ticker + "/bars?timeframe=" + tf + "&start=" + f + "&end=" + t + "&limit=" + str(l) + "&adjustment=all&feed=otc&sort=" + s
      #else:

      if _from > to:
         print("Fatal: From time higher than To time!", _from, to)

      url = "https://data.alpaca.markets/v2/stocks/" + ticker + "/bars?timeframe=" + timeframe + "&start=" + _from + "&end=" + to + "&limit=" + str(limit) + "&adjustment=all&feed=sip&sort=" + sort

      while True:
         try:
            response = self.session.get(url, timeout=1)
            if response.status_code == 200:

               if result_queue:
                  result_queue.put((ticker, response.json()))
               else
                  return response.json()

            response.raise_for_status()

         except requests.exceptions.Timeout:
            pass
         except requests.exceptions.RequestException as e:
            pass

   # This assumes you are using a margin account.
   # Dont use
   async def buy(ticker, price, quantity=None):
      if ticker in self.trades["brokerage"]:
         special = True
      else:
         special = False
         self.trades["brokerage"][ticker] = {}

      account = self.session.get("https://api.alpaca.markets/v2/account").json()
      bp = float(account["cash"])
      if bp > float(config["settings"]["wager_bp"]["value"]):
         bp = float(config["settings"]["wager_bp"]["value"])

      ob = self.robinhood.get_pricebook_by_symbol(ticker)
      price = ob["asks"][1]["price"]["amount"]

      if quantity:
         shares = quantity
      else:
         shares = math.floor(bp * float(config["settings"]["wager_percent"]["value"])/float(price))

      if self.trades["brokerage"][ticker].get("shares"):
         self.trades["brokerage"][ticker]["shares"] += shares
      else:
         self.trades["brokerage"][ticker]["shares"] = shares

      if account["daytrade_count"] < 3 and self.trades["brokerage"]["daytrades"] < 3:
         self.session.headers["Content-Type"] = "application/json"

         if get_market_hours_type() == "market":
            payload = {
               "side": "buy",
               "type": "market",
               "time_in_force": "day",
               "qty": str(shares),
               "symbol": ticker
            }
            # if not trading the same security
            if not special:
               self.trades["brokerage"]["daytrades"] += 1
            print("BUYING MARKET ORDER", ticker, shares, price)
            response = session.post("https://api.alpaca.markets/v2/orders", json=payload)

         else:
            payload = {
               "side": "buy",
               "type": "limit",
               "time_in_force": "day",
               "qty": str(shares),
               "limit_price": str(price),
               "extended_hours": True,
               "symbol": ticker
            }

            if not special:
               self.trades["brokerage"]["daytrades"] += 1
            print("alpaca: buying:", ticker, shares, price)
            response = requests.post("https://api.alpaca.markets/v2/orders", json=payload, headers=headers)
            #print(response.text)

   async def sell(ticker, price, quantity=None):
      self.session.headers["Content-Type"] = "application/json"

      if quantity:
         shares = quantity
      elif self.trades["brokerage"][ticker].get("shares"):
         shares = self.trades["brokerage"][ticker]["shares"]
      else:
         return

      if tools.get_market_hours_type() == "market":
         payload = {
            "side": "sell",
            "type": "market",
            "time_in_force": "day",
            "qty": str(shares),
            "symbol": ticker
         }
         response = self.session.post("https://api.alpaca.markets/v2/orders", json=payload)
         print("alpaca: Selling Market Order", ticker, shares, str(price))
      else:
         ob = self.robinhood.get_pricebook_by_symbol(ticker)
         price = ob["bids"][1]["price"]["amount"]
         payload = {
            "side": "sell",
            "type": "limit",
            "time_in_force": "day",
            "qty": str(shares),
            "limit_price": str(price),
             "extended_hours": True,
             "symbol": ticker
         }
         response = self.session.post("https://api.alpaca.markets/v2/orders", json=payload)
         print("alpaca: Selling Limit Order", ticker, str(shares), str(price))

#######del trades["alpaca"][ticker]


   def get_otc_status(self, ticker):
      data = self.session.get("https://api.alpaca.markets/v2/assets/" + ticker, headers=self.headers).json()
      return data["exchange"]

   def get_trades(self, ticker):
      return self.session.get("https://data.alpaca.markets/v2/stocks/" + ticker + "/trades/latest?feed=sip").json()

