import requests, os, json, pickle

class Robinhood:
   def __init__(self, user, password, device_token, user_agent):
   #def __init__(self, config):
      #self.config = config

      self.user = user
      self.password = password
      self.device_token = device_token
      self.user_agent = user_agent

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
         "User-Agent": self.user_agent
      }
      self.login(self.user, self.password, self.device_token)
      #self.login(self.config["robinhood"]["user"], self.config["robinhood"]["password"], self.config["robinhood"]["device_token"])

      #not supporting this
      #self.trades = {"brokerage": {"daytrades": 0}, "roth": {"daytrades": 0}, "traditional": {"daytrades": 0}}

      self.trades = {"brokerage": {}, "roth": {}, "traditional": {}}
      if os.path.exists("robinhood_trades.pickle"):
         with open("robinhood_trades.pickle", 'rb') as file:
            self.trades = pickle.load(file)

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

   def login(self, username=None, password=None, device_token=None):
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
               print(res)
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
      if workflow:
         if workflow.get("verification_workflow"):
            payload_temp = {
               "device_id": device_token,
                "flow": "suv",
                "input": { "workflow_id": workflow["verification_workflow"]["id"] }
            }

            self.session.headers["Content-Type"] = "application/json"
            inquiry_id = self.session.post("https://api.robinhood.com/pathfinder/user_machine/", data=json.dumps(payload_temp), timeout=5).json()
            data = self.session.get("https://api.robinhood.com/pathfinder/inquiries/" + inquiry_id["id"] + "/user_view/").json()

            if data["context"]["sheriff_challenge"]["type"] == "email" or data["context"]["sheriff_challenge"]["type"] == "sms":
               id = data["context"]["sheriff_challenge"]["id"]
               code = input("Check your email/sms for the verification code and input here. ")
               payload_challenge = {
                  "response": code
               }

               data = self.session.post("https://api.robinhood.com/challenge/" + id + "/respond/", data=json.dumps(payload_challenge)).json()

            else:

               pause = input("Check your robinhood app for notification then press enter when accepted.")

            payload_temp = {"sequence":0,"user_input":{"status":"continue"}}
            data = self.session.post("https://api.robinhood.com/pathfinder/inquiries/" + inquiry_id["id"] + "/user_view/", data=json.dumps(payload_temp), timeout=5).json()
            self.session.headers["Content-Type"] = "application/x-www-form-urlencoded; charset=utf-8"

            data = self.session.post("https://api.robinhood.com/oauth2/token/", data=payload).json()
            #print(data)

         # Update Session data with authorization or raise exception with the information present in data.
         if 'access_token' in data:
            token = '{0} {1}'.format(data['token_type'], data['access_token'])
            self.session.headers["Authorization"] = token
            #data['detail'] = "logged in with brand new authentication code."
            with open(creds_file, 'wb') as f:
                pickle.dump({'token_type': data['token_type'],
                             'access_token': data['access_token'],
                             'refresh_token': data['refresh_token'],
                             'device_token': payload['device_token']}, f)
         else:
            raise Exception(str(data))
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

   def load_account_profile(self, type):

      url = 'https://api.robinhood.com/accounts/'+self.config["robinhood"][type + "_account_number"]
      return self.session.get(url).json()

#
#   def aggregate_url(account_number):
#       if account_number:
#           return('https://api.robinhood.com/options/aggregate_positions/?account_numbers='+account_number)
#       else:
#           return('https://api.robinhood.com/options/aggregate_positions/')
#
#   def option_historicals_url(id):
#       return('https://api.robinhood.com/marketdata/options/historicals/{0}/'.format(id))
#
#
#
#
#   def option_orders_url(orderID=None, account_number=None):
#       url = 'https://api.robinhood.com/options/orders/'
#       if orderID:
#           url += '{0}/'.format(orderID)
#       if account_number:
#           url += ('?account_numbers='+account_number)
#
#       return url
#
#
#   def option_positions_url(account_number):
#       if account_number:
#           return('https://api.robinhood.com/options/positions/?account_numbers='+account_number)
#       else:
#           return('https://api.robinhood.com/options/positions/')
#
#
#   def marketdata_options_url():
#   ('https://api.robinhood.com/marketdata/options/')
#
#

   def get_open_option_positions(account_number=None, info=None):
       payload = {'nonzero': 'True'}
       return request_get('https://api.robinhood.com/options/positions/?account_numbers='+account_number, 'pagination', payload)

   def get_pricebook_by_symbol(self, symbol):
      id = self.get_id(symbol)
      a = self.session.get("https://api.robinhood.com/marketdata/pricebook/snapshots/{0}/".format(id)).json()
      return a

   def order_buy_market(self, symbol, quantity, account_number=None, timeInForce='gtc', extendedHours=False):
      return self.order(symbol, quantity, "buy", account_number, None, timeInForce, extendedHours)

   def order_sell_market(self, symbol, quantity, account_number=None, timeInForce='gtc', extendedHours=False):
      return self.order(symbol, quantity, "sell", account_number, None, timeInForce, extendedHours)

   def order_buy_limit(self, symbol, quantity, limitPrice, account_number=None, timeInForce='gtc', extendedHours=False):
      return self.order(symbol, quantity, "buy", account_number, limitPrice, timeInForce, extendedHours)

   def order_sell_limit(self, symbol, quantity, limitPrice, account_number=None, timeInForce='gtc', extendedHours=False):
      return self.order(symbol, quantity, "sell", account_number, limitPrice, timeInForce, extendedHours)
# browser
#{"account":"https://api.robinhood.com/accounts/4/","ask_price":"10.000000","bid_ask_timestamp":"2024-02-27T13:10:02Z","bid_price":"9.210000","instrument":"https://api.robinhood.com/instruments/72370071-a57a-4335-ad01-312ce75ad269/","quantity":"25","market_hours":"extended_hours","order_form_version":4,"ref_id":"b7b","side":"buy","symbol":"SWIN","time_in_force":"gfd","trigger":"immediate","type":"limit","preset_percent_limit":"0.05","price":"10.08"}
#{'account': 'https://api.robinhood.com/accounts/4/',                                                                                         'instrument': 'https://api.robinhood.com/instruments/72370071-a57a-4335-ad01-312ce75ad269/', 'market_hours': 'extended_hours', 'order_form_version': 4, 'preset_percent_limit': '0.05', 'price': 10.08, 'quantity': 2, 'ref_id': '382', 'side': 'buy', 'symbol': 'SWIN', 'time_in_force': 'gfd', 'trigger': 'immediate', 'type': 'limit', 'extended_hours': True}
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

      #ob = self.get_pricebook_by_symbol(symbol)

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
      return(data)


   async def sell_all_ticker_trades(self, ticker, price, q=None):
      if ticker in self.trades["traditional"]:
         await sell_traditional(ticker, round(price, 4), q)
         await alerts.send_gmail("Selling On Robinhood Trad. IRA. Ticker: " + ticker + " Price: " + str(price))

      if ticker in self.trades["roth"]:
         await sell_roth(ticker, round(price, 4), q)
         await alerts.send_gmail("Selling On Robin Hood Roth IRA. Ticker: " + ticker + " Price: " + str(price))

      if ticker in self.trades["brokerage"]:
         await sell_brokerage(ticker, round(price, 4), q)
         await alerts.send_gmail("Selling On Robin Hood. Ticker: " + ticker + " Price: " + str(price))

      with open("robinhood_trades.pickle", 'wb') as file:
         pickle.dump(trades, file)

   # to delete make sure all shares are sold
   async def sell(self, type, ticker, price, q=None):
      if q:
         shares = int(q)
      elif self.trades[type][ticker].get("shares"):
         shares = int(self.trades[type][ticker]["shares"])
      else:
         print("robinhood: sell() no shares to sell")
         return

      if tools.get_market_hours_type() == "market":
         self.order_sell_market(symbol=ticker, quantity=shares, account_number=config["robinhood"][type + "_account_number"])
         print(type + ": Selling Market Order", ticker, shares, str(price))
      else:
         ob = self.get_pricebook_by_symbol(ticker)
         price = ob["bids"][1]["price"]["amount"]
         self.order_sell_limit(ticker, shares, float(price), account_number=config["robinhood"][type + "_account_number"], extendedHours=True)
         print(type + ": Selling Limit Order", ticker, str(shares), str(price))

      #del self.trades["brokerage"][ticker]

   async def buy(self, type, ticker, price=None, q=None):
      '''
       type: account type; brokerage, roth, traditional
      '''
#      if ticker in self.trades[type]:
#         special = True
#      else:
#         special = False
#         self.trades[type][ticker] = {}

      if not ticker in self.trades[type]:
         self.trades[type][ticker] = {}

      account = self.load_account_profile(account_number=config["robinhood"][type + "_account_number"])
      bp = float(account["buying_power"])
      if bp > float(config["settings"]["wager_bp"]["value"]):
         bp = float(config["settings"]["wager_bp"]["value"])

      # todo check the spread
      ob = self.get_pricebook_by_symbol(ticker)
      price = ob["asks"][1]["price"]["amount"]

      if q:
         shares = q
      else:
         shares = math.floor(bp * float(config["settings"]["wager_percent"]["value"])/float(price))

      if self.trades[type][ticker].get("shares"):
         self.trades[type][ticker]["shares"] += shares
      else:
         self.trades[type][ticker]["shares"] = shares

# Not supporting margin accounts under 25k
#      if account["type"] == "margin":
#          if float(account["portfolio_cash"]) < 25000:
#             daytrades = self.get_day_trades(account=config["robinhood"][type + "_account_number"])
#             if len(daytrades["equity_day_trades"]) < 3 and trades[type]["daytrades"] < 3 and not daytrades["option_day_trades"]:
#                if tools.get_market_hours_type() == "market":
#                   if not special:
#                      self.trades["rh_ira"]["daytrades"] += 1
#                   data = self.order_buy_market(symbol=ticker, quantity=shares, account_number=config["robinhood"]["ira_account_number"])
#                   print("BUYING MARKET ORDER", ticker, shares, price)
#                else:
#                   if not special:
#                      self.trades["rh_ira"]["daytrades"] += 1
#                   print("BUYING LIMIT ORDER", ticker, shares, price)
#                   data = self.order_buy_limit(symbol=ticker, quantity=shares, limitPrice=float(price), account_number=config["robinhood"]["ira_account_number"], extendedHours=True)

      if account["type"] == "cash" or (account["type"] == "margin" and float(account["portfolio_cash"]) >= 25000):
         if tools.get_market_hours_type() == "market":
            self.order_buy_market(ticker, shares, account_number=config["robinhood"][type + "_account_number"])
            print("BUYING MARKET ORDER", ticker, str(shares), str(price))
         else:
            ob = self.get_pricebook_by_symbol(ticker)
            price = ob["asks"][1]["price"]["amount"]
            self.order_buy_limit(ticker, shares, float(price), account_number=config["robinhood"][type + "_account_number"], extendedHours=True)
            print("robinhood: " + type + ": BUYING LIMIT ORDER", ticker, str(shares), str(price))
      else:
         if float(account["portfolio_cash"]) < 25000:
            print("Not Supporting margin accounts under 25k")

   async def buy_roth(self, ticker, price, q=None):
      self.buy("roth", price, q)

   async def buy_traditional(self, ticker, price, q=None):
      self.buy("traditional", price, q)

   async def buy_brokerage(self, price, q=None):
      self.buy("brokerage", price, q)

   async def sell_roth(self, ticker, price, q=None):
      self.sell("roth", price, q)

   async def sell_traditional(self, ticker, price, q=None):
      self.sell("traditional", price, q)

   async def sell_brokerage(self, price, q=None):
      self.sell("brokerage", price, q)

   def get_option_chains(self, symbol):
      #{
      #"next":null,
      #"previous":null,
      #"results":
      # [
      #   {
      #      "id":"9772cebc-34ca-4dfc-af08-9870b6368940",
      #      "symbol":"NEM",
      #      "can_open_position":true,
      #      "cash_component":null,
      #      "expiration_dates":["2024-08-02","2024-08-09","2024-08-16","2024-08-23","2024-08-30","2024-09-06","2024-09-20","2024-10-18","2024-12-20","2025-01-17","2025-03-21","2025-06-20","2026-01-16","2026-12-18"],
      #      "trade_value_multiplier":"100.0000","underlying_instruments":[{"id":"d4464262-9bcc-40ad-bc18-b610a4d32875","instrument":"https:\/\/api.robinhood.com\/instruments\/adbc3ce0-dd0d-4a7a-92e0-88c1f127cbcb\/","quantity":100}],
      #      "min_ticks":{"above_tick":"0.05","below_tick":"0.01","cutoff_price":"3.00"},"late_close_state":"disabled"
      #   }
      # ]
      #}
      #return self.session.get('https://api.robinhood.com/options/chains/{0}/'.format(id_for_chain(symbol)))
      return self.session.get("https://api.robinhood.com/options/chains/?account_number=" + self.config["robinhood"]["brokerage_account_number"] + "&equity_symbol=" + symbol).json()

   def get_instruments(self, id, chain, dates, type):
      #type: call/put

      #{
      #"next":null,
      #"previous":null,
      #"results":
      #[
      #{
      #"chain_id":"9772cebc-34ca-4dfc-af08-9870b6368940",
      #"chain_symbol":"NEM","created_at":"2024-06-13T01:05:14.465048Z",
      #"expiration_date":"2024-08-02",
      #"id":"f963060b-a8a8-4924-bfcf-155f87f12fe6",
      #"issue_date":"2024-06-13",
      #"min_ticks":{"above_tick":"0.05","below_tick":"0.01","cutoff_price":"3.00"},
      #"rhs_tradability":"tradable",
      #"state":"active",
      #"strike_price":"46.0000",
      #"tradability":"tradable",
      #"type":"call",
      #"updated_at": "2024-06-13T01:05:14.465051Z",
      #"url":"https:\/\/api.robinhood.com\/options\/instruments\/f963060b-a8a8-4924-bfcf-155f87f12fe6\/",
      #"sellout_datetime":"2024-08-02T19:30:00+00:00",
      #"long_strategy_code":"f963060b-a8a8-4924-bfcf-155f87f12fe6_L1", "short_strategy_code":"f963060b-a8a8-4924-bfcf-155f87f12fe6_S1"},
      # ...

      # Closest expiration date to today's date
      if len(dates) > 1:
        edates = ",".join(dates)
      else:
        edates = dates[0]
      return self.session.get("https://api.robinhood.com/options/instruments/?account_number=" + self.config["robinhood"]["brokerage_account_number"] + "&chain_id=" + id + "&expiration_dates=" + edates + "&state=active&type=" + type).json()

   def get_options_market_data(self, id):
      #{ "results": [{"adjusted_mark_price":"10.950000", "adjusted_mark_price_round_down":"10.950000",
      #"ask_price":"12.350000", "ask_size":78,
      #"bid_price":"9.550000", "bid_size":77,
      #"break_even_price":"49.050000",
      #"high_price":null,
      #"instrument":"https://api.robinhood.com/options/instruments/f94add9f-cb61-4edf-8dae-ab2cdaec00d5/",
      #"instrument_id":"f94add9f-cb61-4edf-8dae-ab2cdaec00d5",
      #"last_trade_price":null, "last_trade_size":null, "low_price":null, "mark_price":"10.950000",
      #"open_interest":0,
      #"previous_close_date":"2024-07-30",
      #"previous_close_price":"12.530000",
      #"updated_at":"2024-07-31T19:51:37.304504832Z",
      #"volume":0,
      #"symbol":"NEM",
      #"occ_symbol":"NEM   240809P00060000",
      #"state":"active",
      #"chance_of_profit_long":"0.512351",
      #"chance_of_profit_short":"0.487649",
      #"delta":"-0.890820","gamma":"0.019683","implied_volatility":"0.918135","rho":"-0.007031","theta":"-0.065305","vega":"0.013654","pricing_model":"Bjerksund-Stensland 1993",
      #"high_fill_rate_buy_price":"11.448000",
      #"high_fill_rate_sell_price":"10.451000",
      #"low_fill_rate_buy_price":"10.034000",
      #"low_fill_rate_sell_price":"11.865000"}]}
      return self.session.get("https://api.robinhood.com/marketdata/options/?ids=" + id).json()


   def option_order(self, account, symbol, type, direction="debit"):

      payload = {
      "account":"https://api.robinhood.com/accounts/" + account + "/",
      "check_overrides":["override_no_bid_price"],
      #"client_ask_at_submission":"0.01",
      #"client_bid_at_submission":"0",
      "direction": direction,
      "form_source":"option_chain",
      "legs":[
       {"option":"https://api.robinhood.com/options/instruments/c310fdd7-b520-4d9f-a5cf-63a05685bc44/",
       "position_effect":"open",
       "ratio_quantity":1,
       "side":"buy"}
       ],
      "override_day_trade_checks":false,
      "price":"0.01",
      "quantity":"1",
      "ref_id":"1f289107-28b5-448b-a875-833d37496239",
      "time_in_force":"gfd",
      "trigger":"immediate",
      "type":"limit"}

   def buy_call(self, symbol):
      #if not chain
      chain = self.get_option_chains(symbol)
      instrument = self.get_instruments(chain["results"][0]["id"], chain, chain["results"][0]["expiration_dates"][0], "call")
      for entry in range(len(instrument["results"])):
         data = self.get_options_market_data(instrument["results"][entry])
         print(data)
         return data

      #result = ",".join(map(str, numbers))
#https://api.robinhood.com/options/orders/66b/
#{"account_number":"",
#"cancel_url":null,"canceled_quantity":"1.00000",
#"created_at":"2024-08-08T14:51:08.336436Z","direction":"credit","id":"",
#"legs":[{"executions":[],"id":"66b4db5c-ac69-4777-950e-9b1e1ac583e9",
#"option":"https:\/\/api.robinhood.com\/options\/instruments\/a94999db-fa8a-4117-aace-cb94e3820aab\/",
#"position_effect":"close","ratio_quantity":1,"side":"sell","expiration_date":"2024-08-08","strike_price":"536.0000","option_type":"call","long_strategy_code":"a94999db-fa8a-4117-aace-cb94e3820aab_L1",
#"short_strategy_code":"a94999db-fa8a-4117-aace-cb94e3820aab_S1"}],"pending_quantity":"0.00000","premium":"8.00000000","processed_premium":"0","net_amount":"0","net_amount_direction":"credit","price":"0.08000000","processed_quantity":"0.00000","quantity":"1.00000","ref_id":"","regulatory_fees":"0","state":"cancelled","time_in_force":"gfd","trigger":"immediate","type":"limit","updated_at":"2024-08-08T18:04:11.468888Z","chain_id":"c277b118-58d9-4060-8dc5-a3b5898955cb","chain_symbol":"SPY","response_category":null,"opening_strategy":null,"closing_strategy":"long_call","stop_price":null,"form_source":"strategy_detail","client_bid_at_submission":"-0.09000000","client_ask_at_submission":"-0.08000000","client_time_at_submission":null,
#"average_net_premium_paid":"0.00000000","estimated_total_net_amount":"0",
#"estimated_total_net_amount_direction":"credit","is_replaceable":false}
