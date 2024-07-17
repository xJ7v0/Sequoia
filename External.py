import json, requests, os, pytz

#from os import path
from Internal import alerts, tools

with open("config.json", "r") as jsonfile: config = json.load(jsonfile)

'''
##############
# Brokerages #
##############
'''
class Alpaca:
   def __init__(self):
      self.session = requests.Session()
      self.headers = {
         "accept": "application/json",
         "APCA-API-KEY-ID": config["alpaca"]["api_key"],
         "APCA-API-SECRET-KEY": config["alpaca"]["secret"]
      }

   def get_otc_status(self, ticker):
      data = self.session.get("https://api.alpaca.markets/v2/assets/" + ticker, headers=self.headers).json()
      return data["exchange"]


class Robinhood:
   def __init__(self):
      self.session = requests.Session()
      self.session.headers = {
         "Accept": "*/*",
         "Accept-Encoding": "gzip,deflate,br",
         "Accept-Language": "en-US,en;q=1",
         "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
         "X-Robinhood-API-Version": "1.431.4",
         "Connection": "keep-alive",
         "Host": "api.robinhood.com",
         "Origin": "https://robinhood.com",
         "Referer": "https://robinhood.com/",
         "User-Agent": config["settings"]["user_agent"]["value"]
     }

      self.trades = {"brokerage": {"daytrades": 0}, "roth": {"daytrades": 0}}
      self.trades["brokerage"]["daytrades"] = len(self.get_day_trades(account=config["robinhood"]["account_number"])["equity_day_trades"])
      self.trades["roth"]["daytrades"] = len(self.get_day_trades(account=config["robinhood"]["ira_account_number"])["equity_day_trades"])

   def round_price(self, price):
      price = float(price)
      if price <= 1e-2:
         returnPrice = round(price, 6)
      elif price < 1e0:
         returnPrice = round(price, 4)
      else:
         returnPrice = round(price, 2)
      return returnPrice

   def get_day_trades(self, account=None):
      return self.session.get('https://api.robinhood.com/accounts/{0}/recent_day_trades/'.format(account)).json()

# def get(self, url, payload=None):
#    if payload:
#        print(self.session.get(url).json())
#    else:
#        print(self.session.get(url, params=payload).json())


   def login(self, username=None, password=None, mfa_code=None, device_token=None):
      creds_file = "robinhood.pickle"
      payload = {
         'client_id': 'c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS',
         'create_read_only_secondary_token': "false",
         'device_token': device_token,
         'expires_in': 86400,
         'grant_type': 'password',
         'long_session': "true",
         'password': password,
         'scope': "internal",
         'token_request_path': "/login/",
         'username': username,
      }

      if os.path.isfile(creds_file):
         # Loading pickle file will fail if the acess_token has expired.
         try:
            with open(creds_file, 'rb') as f:
               pickle_data = pickle.load(f)
               access_token = pickle_data['access_token']
               token_type = pickle_data['token_type']
               refresh_token = pickle_data['refresh_token']
               self.session.headers["Authorization"] = '{0} {1}'.format(token_type, access_token)
               # Try to load account profile to check that authorization token is still valid.
               res = self.session.get("https://api.robinhood.com/accounts/")
               # Raises exception is response code is not 200.
               res.raise_for_status()
               return
#               return({'access_token': access_token, 'token_type': token_type,
#                       'expires_in': "86400", 'scope': "internal", 'detail': 'logged in using authentication in {0}'.format(creds_file),
#                       'backup_code': None, 'refresh_token': refresh_token})
         except:
            print("ERROR: There was an issue loading pickle file. Authentication may be expired - logging in normally.")
            self.session.headers["Authorization"] = None

      #json_data = json.dumps(payload)
      workflow = self.session.post("https://api.robinhood.com/oauth2/token/", data=payload, timeout=10).json()
      print(workflow)
      if workflow:
         if workflow.get("verification_workflow"):
            payload_temp = {
               "device_id": device_token,
                "flow": "suv",
                "input": { "workflow_id": workflow["verification_workflow"]["id"] }
            }

            #o = self.session.options("https://api.robinhood.com/pathfinder/user_machine/", timeout=5)
            #print(o)

            self.session.headers["Content-Type"] = "application/json"
            inquiry_id = self.session.post("https://api.robinhood.com/pathfinder/user_machine/", data=json.dumps(payload_temp), timeout=5).json()
            data = self.session.get("https://api.robinhood.com/pathfinder/inquiries/" + inquiry_id["id"] + "/user_view/").json()

            pause = input('Check your robinhood app for notification then press enter when accepted.')

            payload_temp = {"sequence":0,"user_input":{"status":"continue"}}
            data = self.session.post("https://api.robinhood.com/pathfinder/inquiries/" + inquiry_id["id"] + "/user_view/", data=json.dumps(payload_temp), timeout=5).json()
            data = self.session.post("https://api.robinhood.com/oauth2/token/", data=payload).json()

         # Update Session data with authorization or raise exception with the information present in data.
         if 'access_token' in data:
            token = '{0} {1}'.format(data['token_type'], data['access_token'])
            self.session.headers["Authorization"] = token
            data['detail'] = "logged in with brand new authentication code."
            with open(creds_file, 'wb') as f:
                pickle.dump({'token_type': data['token_type'],
                             'access_token': data['access_token'],
                             'refresh_token': data['refresh_token'],
                             'device_token': payload_l['device_token']}, f)
         else:
            raise Exception(data['detail'])
      else:
         raise Exception('Error: Trouble connecting to robinhood API. Check internet connection.')
      return(data)

   def get_id(self, symbol):
     i = 0
     results = self.session.get("https://api.robinhood.com/instruments/?active_instruments_only=false&symbol=" + symbol).json()["results"]
     while i < len(results):
        if results[i]["type"] == "stock":
           return results[i]["id"]
        i += 1

     print("Fatal: Symbol is not a stock!")

   def load_account_profile(self, account_number):
      url = 'https://api.robinhood.com/accounts/'+account_number
      return self.session.get(url).json()

   def get_pricebook_by_symbol(self, symbol):
      id = self.get_id(symbol)
      a = self.session.get("https://api.robinhood.com/marketdata/pricebook/snapshots/{0}/".format(id)).json()
      return a

   def get_option_chains(self, symbol):
      return self.session.get('https://api.robinhood.com/options/chains/{0}/'.format(id_for_chain(symbol)))

   def order_buy_market(self, symbol, quantity, account_number=None, timeInForce='gtc', extendedHours=False):
      return self.order(symbol, quantity, "buy", account_number, None, timeInForce, extendedHours)

   def order_sell_market(self, symbol, quantity, account_number=None, timeInForce='gtc', extendedHours=False):
      return self.order(symbol, quantity, "sell", account_number, None, timeInForce, extendedHours)

   def order_buy_limit(self, symbol, quantity, limitPrice, account_number=None, timeInForce='gtc', extendedHours=False):
      return self.order(symbol, quantity, "buy", account_number, limitPrice, timeInForce, extendedHours)

   def order_sell_limit(self, symbol, quantity, limitPrice, account_number=None, timeInForce='gtc', extendedHours=False):
      return self.order(symbol, quantity, "sell", account_number, limitPrice, timeInForce, extendedHours)
# browser
#{"account":"https://api.robinhood.com/accounts/406984328/","ask_price":"10.000000","bid_ask_timestamp":"2024-02-27T13:10:02Z","bid_price":"9.210000","instrument":"https://api.robinhood.com/instruments/72370071-a57a-4335-ad01-312ce75ad269/","quantity":"25","market_hours":"extended_hours","order_form_version":4,"ref_id":"b7baa87d-287b-4dbc-9c23-3c216649267d","side":"buy","symbol":"SWIN","time_in_force":"gfd","trigger":"immediate","type":"limit","preset_percent_limit":"0.05","price":"10.08"}
#{'account': 'https://api.robinhood.com/accounts/406984328/',                                                                                         'instrument': 'https://api.robinhood.com/instruments/72370071-a57a-4335-ad01-312ce75ad269/', 'market_hours': 'extended_hours', 'order_form_version': 4, 'preset_percent_limit': '0.05', 'price': 10.08, 'quantity': 2, 'ref_id': '38206b7a-a20d-481d-afcc-fdd2c701f234', 'side': 'buy', 'symbol': 'SWIN', 'time_in_force': 'gfd', 'trigger': 'immediate', 'type': 'limit', 'extended_hours': True}
   def order(self, symbol, quantity, side, account_number=None, limitPrice=None, timeInForce='gtc', extendedHours=False, market_hours='regular_hours'):
      orderType = "market"
      trigger = "immediate"
      if side == "buy":
         priceType = "ask_price"
      else:
         priceType = "bid_price"

      if extendedHours == True:
         market_hours = "extended_hours"
         timeInForce="gfd"
         orderType = "limit"

      if limitPrice:
         price = self.round_price(limitPrice)
         orderType = "limit"
#      else:
#         price = self.round_price(next(iter(get_latest_price(symbol, priceType, extendedHours)), 0.00))

      #ob = r.get_pricebook_by_symbol(symbol)

	#"ask_price": "0.280000",
	#"bid_price": "0.220000",
	#"bid_ask_timestamp": "2024-01-26T22:01:23Z",

      payload = {
         'account': "https://api.robinhood.com/accounts/" + account_number + "/",
         'instrument': "https://api.robinhood.com/instruments/" + self.get_id(symbol) + "/",
         'market_hours': market_hours,
         'order_form_version': 4,
         'preset_percent_limit': '0.05',
         'price': price,
         'quantity': quantity,
         'ref_id': str(uuid4()),
         'side': side,
         'symbol': symbol,
         'time_in_force': timeInForce,
         'trigger': trigger,
         'type': orderType,
         'extended_hours': extendedHours
      }

      # adjust market orders
      if orderType == 'market':
         del payload['extended_hours']

      if market_hours == 'regular_hours':
         if side == "buy":
            payload['preset_percent_limit'] = "0.05"
            payload['type'] = 'limit'
         # regular market sell
         elif orderType == 'market' and side == 'sell':
            del payload['price']

      self.session.headers['Content-Type'] = 'application/json'
      data = self.session.post("https://api.robinhood.com/orders/", json=payload, timeout=5).json()
      self.session.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=utf-8'
      print(data)
      return(data)


   async def sell(self, ticker, price, q=None):
      #with open("trades.pickle", 'rb') as file:
      #   self.trades = pickle.load(file)

      if ticker in self.trades["roth"]:
         await sell_roth(ticker, round(price, 4), q)
         await alerts.send_gmail("Selling On Robin Hood Roth IRA. Ticker: " + ticker + " Price: " + str(price))
      if ticker in self.trades["brokerage"]:
         await sell_brokerage(ticker, round(price, 4), q)
         #await send_gmail("Selling On Robin Hood. Ticker: " + ticker + " Price: " + str(price))
      #elif ticker in trades["alpaca"]:
      #   await sell_alpaca(ticker, round(price, 4), q)
         #await send_gmail("Selling On Alpaca. Ticker: " + ticker + " Price: " + str(price))

#      with open("trades.pickle", 'wb') as file:
#         pickle.dump(trades, file)

   async def sell_brokerage(self, ticker, price, q=None):
      if q:
         shares = int(q)
      elif self.trades["brokerage"][ticker].get("shares"):
         shares = int(self.trades["brokerage"][ticker]["shares"])
      else:
         return

      if get_market_hours_type() == "market":
         self.order_sell_market(symbol=ticker, quantity=shares, account_number=config["robinhood"]["account_number"])
         print("brokerage: Selling Market Order", ticker, shares, str(price))
      else:
         ob = self.get_pricebook_by_symbol(ticker)
         price = ob["bids"][1]["price"]["amount"]
         self.order_sell_limit(ticker, shares, float(price), account_number=config["robinhood"]["account_number"], extendedHours=True)
         print("brokerage: Selling Limit Order", ticker, str(shares), str(price))

      del self.trades["brokerage"][ticker]

   async def sell_roth(self, ticker, price, q=None):
      if q:
         shares = int(q)
      elif self.trades["roth"][ticker].get("shares"):
         shares = int(self.trades["roth"][ticker]["shares"])
      else:
         return

      if get_market_hours_type() == "market":
         self.order_sell_market(symbol=ticker, quantity=shares, account_number=config["robinhood"]["ira_account_number"])
         print("roth: Selling Market Order", ticker, shares, str(price))
      else:
         ob = self.get_pricebook_by_symbol(ticker)
         price = ob["bids"][1]["price"]["amount"]
         self.order_sell_limit(ticker, shares, float(price), account_number=config["robinhood"]["ira_account_number"], extendedHours=True)
         print("roth: Selling Limit Order", ticker, str(shares), str(price))

      del self.trades["roth"][ticker]

   async def buy_roth(self, ticker, price, q=None):
      if ticker in self.trades["roth"]:
         special = True
      else:
         special = False

      self.trades["roth"][ticker] = {}

      account = self.load_account_profile(account_number=config["robinhood"]["ira_account_number"])
      bp = float(account["buying_power"])
      if bp > float(config["settings"]["wager_bp"]["value"]):
         bp = float(config["settings"]["wager_bp"]["value"])

      ob = self.get_pricebook_by_symbol(ticker)
      price = ob["asks"][1]["price"]["amount"]

      if q:
         shares = q
      else:
         shares = math.floor(bp * float(config["settings"]["wager_percent"]["value"])/float(price))

      if self.trades["roth"][ticker].get("shares"):
         self.trades["roth"][ticker]["shares"] += shares
      else:
         self.trades["roth"][ticker]["shares"] = shares

      if account["type"] == "margin":
          if float(account["portfolio_cash"]) < 25000:
             daytrades = self.get_day_trades(account=config["robinhood"]["ira_account_number"])
             if len(daytrades["equity_day_trades"]) < 3 and trades["rh_ira"]["daytrades"] < 3 and not daytrades["option_day_trades"]:
                if tools.get_market_hours_type() == "market":
                   if not special:
                      self.trades["rh_ira"]["daytrades"] += 1
                   data = self.order_buy_market(symbol=ticker, quantity=shares, account_number=config["robinhood"]["ira_account_number"])
                   print("BUYING MARKET ORDER", ticker, shares, price)
                else:
                   if not special:
                      self.trades["rh_ira"]["daytrades"] += 1
                   print("BUYING LIMIT ORDER", ticker, shares, price)
                   data = self.order_buy_limit(symbol=ticker, quantity=shares, limitPrice=float(price), account_number=config["robinhood"]["ira_account_number"], extendedHours=True)

      elif account["type"] == "cash":
         if tools.get_market_hours_type() == "market":
            self.order_buy_market(ticker, shares, account_number=config["robinhood"]["ira_account_number"])
            print("BUYING MARKET ORDER", ticker, str(shares), str(price))
         else:
            ob = self.get_pricebook_by_symbol(ticker)
            price = ob["asks"][1]["price"]["amount"]
            self.order_buy_limit(ticker, shares, float(price), account_number=config["robinhood"]["ira_account_number"], extendedHours=True)
            print("BUYING LIMIT ORDER", ticker, str(shares), str(price))

   async def buy_brokerage(ticker, price, q=None):
      if ticker in self.trades["brokerage"]:
         special = True
      else:
         special = False

      trades["brokerage"][ticker] = {}

      account = self.load_account_profile(account_number=config["robinhood"]["account_number"])
      bp = float(account["buying_power"])
      if bp > float(config["settings"]["wager_bp"]["value"]):
         bp = float(config["settings"]["wager_bp"]["value"])

      ob = self.get_pricebook_by_symbol(ticker)
      price = ob["asks"][1]["price"]["amount"]

      if q:
         shares = q
      else:
         shares = math.floor(bp * float(config["settings"]["wager_percent"]["value"])/float(price))

      if self.trades["brokerage"][ticker].get("shares"):
         self.trades["brokerage"][ticker]["shares"] += shares
      else:
         self.trades["brokerage"][ticker]["shares"] = shares

      if account["type"] == "margin":
          if float(account["portfolio_cash"]) < 25000:
             daytrades = self.get_day_trades(account=config["robinhood"]["account_number"])
             if len(daytrades["equity_day_trades"]) < 3 and trades["rh"]["daytrades"] < 3 and not daytrades["option_day_trades"]:
                if tools.get_market_hours_type() == "market":
                   if not special:
                      self.trades["brokerage"]["daytrades"] += 1
                   data = self.order_buy_market(symbol=ticker, quantity=shares, account_number=config["robinhood"]["account_number"])
                   print("BUYING MARKET ORDER", ticker, shares, price)
                else:
                   if not special:
                      self.trades["brokerage"]["daytrades"] += 1
                   print("BUYING LIMIT ORDER", ticker, shares, price)
                   data = self.order_buy_limit(symbol=ticker, quantity=shares, limitPrice=float(price), account_number=config["robinhood"]["account_number"], extendedHours=True)

      elif account["type"] == "cash":
         if get_market_hours_type() == "market":
            self.order_buy_market(ticker, shares, account_number=config["robinhood"]["account_number"])
            print("BUYING MARKET ORDER", ticker, str(shares), str(price))
         else:
            ob = self.get_pricebook_by_symbol(ticker)
            price = ob["asks"][1]["price"]["amount"]
            self.order_buy_limit(ticker, shares, float(price), account_number=config["robinhood"]["account_number"], extendedHours=True)
            print("BUYING LIMIT ORDER", ticker, str(shares), str(price))


class Symbols:
   def update_symbols():
      if not os.path.exists("./previous_symbols"):
         os.makedirs("./previous_symbols")
      #dest_file = os.path.join(dest_directory, os.path.basename(src_file))
      os.rename("symbols.pickle", "./previous_symbols/symbols_" + datetime.now().strftime("%m-%d-%Y") + ".pickle")
      self.get_symbols()

   def finviz(self):
      symbols_file = "symbols.pickle"
      if os.path.exists(symbols_file) and os.path.getsize(symbols_file) > 0:
         with open(symbols_file, 'rb') as file:
            return pickle.load(file)

      # Market Cap: Under 2B
      # Current Volume: Under 1M
      # Shares Outstanding: Under 10M
      # Price: Under 10
      #url = "https://finviz.com/screener.ashx?v=111&f=cap_smallunder,sh_curvol_u1000,sh_outstanding_u10,sh_price_u10&ft=4&o=-marketcap&r="
      url = config["settings"]["finviz"]["value"]
      headers = {"User-Agent": config["settings"]["user_agent"]["value"]}
      page = requests.get(url + "1", headers=headers)
      tree = html.fromstring(page.content)
      lastpage = tree.xpath('//*[@class="screener-pages"]/text()')[-1]
      symbols = []
      i = 0
      while i < int(lastpage):
         newurl = url + str(i*20+1)
         page = requests.get(newurl, headers=headers)
         tree = html.fromstring(page.content)
         symbols += tree.xpath('//*[@class="tab-link"]/text()')[2:22]
         i += 1

      with open(symbols_file, 'wb') as file:
         pickle.dump(sorted(symbols)[:-9], file)

      # Removes junk
      return sorted(symbols)[:-9]

   async def stockanalysis(self):
      #https://stockanalysis.com/api/screener/s/d/volume.json
      #https://stockanalysis.com/api/screener/s/i
      symbols_file = "symbols.pickle"
      if os.path.exists(symbols_file) and os.path.getsize(symbols_file) > 0:
         with open(symbols_file, 'rb') as file:
            return pickle.load(file)

      d = {}
      dt = []
      headers = {"User-Agent": config["settings"]["user_agent"]["value"]}
      prices = requests.get("https://stockanalysis.com/api/screener/s/d/price.json", headers=headers).json()
      float_ = requests.get("https://stockanalysis.com/api/screener/s/d/float.json", headers=headers).json()
      i = 0
      if prices["status"] == 200:
         while i < len(prices["data"]["data"]):
            if prices["data"]["data"][i][1] <= float(config["settings"]["max_price"]["value"]):
               t = prices["data"]["data"][i][0]
               d[t] = [prices["data"]["data"][i][1]]
            i += 1

         if float_["status"] == 200:
            for ticker in d:
               found = 0
               i = 0
               while i < len(float_["data"]["data"]):
                  if ticker == float_["data"]["data"][i][0]:
                     if float_["data"]["data"][i][1] <= int(config["settings"]["max_float"]["value"]):
                        d[ticker] += [float_["data"]["data"][i][1]]
                     else:
                        dt += [ticker]
                     found = 1
                  i += 1
               if not found:
                  d[ticker] += [None]

            # delete tickers from the dict that dont meat the requirements
            for i in dt:
               del d[i]

      symbols = []
      for i in d:
         symbols.append(i)

      with open(symbols_file, 'wb') as file:
         pickle.dump(symbols, file)

      return symbols

   #https://scanner.tradingview.com/america/scan
   async def get_symbols(self):
      return await stockanalysis()

class Nasdaq:
   def get_earnings():
      headers = {"User-Agent": config["settings"]["user_agent"]["value"]}
      today = datetime.now()
      d = today.strftime('%Y-%m-%d')
      response = requests.get("https://api.nasdaq.com/api/calendar/earnings?date=" + d, headers=headers)
      e = response.json()
      for i in e["data"]["rows"]:
         print(d, "\033[92m", i["symbol"], '\033[0m', i["lastYearEPS"], i["epsForecast"])

class Polygon:
   def scan_current_move_poly(ticker, result_queue, session):
      now = datetime.now(pytz.timezone("EST")).time()
      c = {}
      c = get_poly_data(ticker, get_prev_mins(2), get_timestamp(now.hour, now.minute), 8, session)
      i = 0
      symbols = {}
      if c:
         while i < c["resultsCount"]:
            if get_percentage(c["results"][i]["o"], c["results"][i]["c"]) >= float(config["settings"]["upper_percent"]["value"]):
               symbols[ticker] = c["results"][i]
               result_queue.put(symbols)
            i += 1
   def poly_get(ticker, f, t, l, s, m, ts, session=None):
      # f - from
      # t - to
      # l - limit
      # s - sort
      # m - multiplier
      # ts - timespan
      url = "https://api.polygon.io/v2/aggs/ticker/" + ticker + "/range/" + str(m) + "/" + ts + "/" + str(f) + "/" + str(t) + "?adjusted=true&sort=" + s + "&limit=" + str(l) + "&apiKey=" + config["polygon"]["api_key"]
      if session:
         while True:
            try:
               response = session.get(url, timeout=2)
               if response.status_code == 200:
                  return response.json()
               response.raise_for_status()
            except requests.exceptions.Timeout:
               pass
               #print("The request timed out. Check your network or try again later.")
            except requests.exceptions.RequestException as e:
               pass
               #print(f"An error occurred: {e}")
               #if isinstance(e, requests.exceptions.ConnectTimeout):
               #   print("Connection timeout. Check your network or try again later.")
      else:
         while True:
            try:
               response = requests.get(url, timeout=2)
               if response.status_code == 200:
                  return response.json()
               response.raise_for_status()
            except requests.exceptions.Timeout:
               pass
            except requests.exceptions.RequestException as e:
               pass

   def get_poly_data(ticker, f, t, l, session=None, result_queue=None):
      if f > t:
         print("Fatal: From time higher than To time!", f, t)
      c = poly_get(ticker, f, t, l, "asc", 15, "second", session)
      if result_queue and c:
         result_queue.put((ticker, c))
      else:
         return c

class StockNewsAPI:
   def __init__(self):
      self.old_news_all = {}
      self.session = requests.Session()
      self.session.headers = {
         "Accept": "*/*",
         "Connection": "keep-alive"
      }

   async def get_all_stocknewsapi(self):
      condition = True
      while condition:
         try:
            response = self.session.get("https://stocknewsapi.com/api/v1/category?section=alltickers&cache=false&items=30&page=1&topic=PressRelease&token=" + config["stocknewsapi"]["api_key"], timeout=5)
            if response.status_code == 200:
               n = response.json()
               condition = False
            response.raise_for_status()
         except requests.exceptions.Timeout:
            pass
         #except requests.exceptions.RequestException as e:
         #   pass
         except:
            print("Fatal: Couldn't get a valid response from stocknewsapi.com")
            return

      n["data"].reverse()
      symbols = await Symbols.get_symbols()

      if self.old_news_all != n and self.old_news_all:
         # Extract titles from old_data["data"] items
         old_data_titles = set(item.get("title") for item in self.old_news_all.get("data", []))
         for item in n.get("data", []):
            title = item["title"]
            if title not in old_data_titles:
               for j in enumerate(item["tickers"]):
                  index, ticker = j
                  for k in symbols:
                     if k == ticker:
                        d = int(datetime.strptime(item["date"], "%a, %d %b %Y %H:%M:%S %z").timestamp() * 1000)
                        print(item["date"], "\033[92m", ticker, '\033[0m', title)
                        process = multiprocessing.Process(target=watch_start, args=(ticker,))
                        process.start()

      elif not self.old_news_all:
         i = 0
         while i < len(n["data"]):
            for j in enumerate(n["data"][i]["tickers"]):
               index, ticker = j
               for k in symbols:
                  if k == ticker:
                     d = int(datetime.strptime(n["data"][i]["date"], "%a, %d %b %Y %H:%M:%S %z").timestamp() * 1000)
                     print(n["data"][i]["date"], "\033[92m", ticker, '\033[0m', n["data"][i]["title"])
                     if int(datetime.now(pytz.timezone("EST")).timestamp() * 1000) - 10000 <= d:
                        process = multiprocessing.Process(target=watch_start, args=(ticker,))
                        process.start()

            i += 1
      self.old_news_all = n
      return
