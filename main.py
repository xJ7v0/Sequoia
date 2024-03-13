#!/usr/bin/python3

#########################################################################
#									#
# 	Trade Bot							#
#									#
# Requirements: polygon.io,						#
#		stocknewsapi.com					#
#		Robinhood IRA (subject to change on request)		#
#									#
# Optional: Gmail							#
#									#
#########################################################################

# No point in fixing since we have stocknewsapi:
# fix businesswire
# parse yesterday news for seeking alpha using date stamp from the server (mostly done)
# check for other tickers in news

# Might not need:
# check volume before buying
# get news within 1 day period

# TODO:
# gap up between open[i] and close[i+1]
# check if ticker is currently moving on the websocket before buying
# check if the order went through
# get stocks from IBKR

# check alpaca to make sure it buys in the premarket
# fix robinhood to buy/sell in the premarket
# fix trades[*][ticker]
# make sure orders go through else cancel them and and do it again
# watch multiple tickers
# sell if green candle is 2% then red candle

import asyncio, calendar, certifi, json, math, multiprocessing, os, pickle, pytz, re, requests, signal, schedule, smtplib, socket, ssl, sys, websockets
#import robin_stocks.robinhood as r
import time as t
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from candlestick_chart import Candle, Chart
from datetime import datetime, date, timedelta, time, timezone
from email.mime.text import MIMEText
from lxml import html
from uuid import uuid4
from websockets.client import connect, WebSocketClientProtocol
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

# Limit to get polygon data based on how many minutes there is in the market hours type
PRE_LIMIT = 350*4
MARKET_LIMIT = 400*4
POST_LIMIT = 250*4

# Time when each market type starts for hours and minutes
#PRE_H = 4
#PRE_M = 0
#MARKET_H = 9
#MARKET_M = 30
#POST_H = 16
#POST_M = 0
#CLOSE_H = 20
#CLOSE_M = 0

with open("config.json", "r") as jsonfile: config = json.load(jsonfile)

'''
##################
# Stock News API #
##################
'''

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
         except requests.exceptions.RequestException as e:
            pass

      n["data"].reverse()
      symbols = await get_symbols()

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

'''
#############
# Robinhood #
#############
'''
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

   def round_price(self, price):
      price = float(price)
      if price <= 1e-2:
         returnPrice = round(price, 6)
      elif price < 1e0:
         returnPrice = round(price, 4)
      else:
         returnPrice = round(price, 2)
      return returnPrice

   def get_day_trades(self, info=None, account=None):
      return self.session.get('https://api.robinhood.com/accounts/{0}/recent_day_trades/'.format(account)).json()

   def respond_to_challenge(self, challenge_id, sms_code):
      url = 'https://api.robinhood.com/challenge/{0}/respond/'.format(challenge_id)
      payload = { 'response': sms_code }
      return(self.session.post(url, data=payload))

# def get(self, url, payload=None):
#    if payload:
#        print(self.session.get(url).json())
#    else:
#        print(self.session.get(url, params=payload).json())


   def login(self, username=None, password=None, mfa_code=None, device_token=None):
      creds_file = "robinhood.pickle"
      payload = {
         'client_id': 'c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS',
         'create_read_only_secondary_token': "true",
         'device_token': device_token,
         'expires_in': 86400,
         'grant_type': 'password',
         'long_session': "true",
         'password': password,
         'scope': "internal",
         'token_request_path': "/login",
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
               #res = self.session.get("https://api.robinhood.com/positions/")
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
      data = self.session.post("https://api.robinhood.com/oauth2/token/", data=payload, timeout=18).json()
      if data:
         if data.get("challenge"):
            challenge_id = data['challenge']['id']
            sms_code = input('Check your robinhood app for notification then press enter when accepted')
#            res = self.respond_to_challenge(challenge_id, sms_code)
#            while 'challenge' in res and res['challenge']['remaining_attempts'] > 0:
#               sms_code = input('That code was not correct. {0} tries remaining. Please type in another code: '.format(res['challenge']['remaining_attempts']))
#               res = self.respond_to_challenge(challenge_id, sms_code)
            self.session.headers["X-ROBINHOOD-CHALLENGE-RESPONSE-ID"] = challenge_id
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
                             'device_token': payload['device_token']}, f)
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

'''
###########
# Globals #
###########
'''
r = Robinhood()
login = r.login(config["robinhood"]["user"], config["robinhood"]["password"], device_token=config["robinhood"]["device_token"])

headers = {
   "accept": "application/json",
   "APCA-API-KEY-ID": config["alpaca"]["api_key"],
   "APCA-API-SECRET-KEY": config["alpaca"]["secret"]
}

trades = {"rh": {"daytrades": 0}, "rh_ira": {"daytrades": 0}, "alpaca": {"daytrades": 0}, "ibkr": {"daytrades": 0}, "ibkr_ira": {"daytrades": 0}}
trades["rh"]["daytrades"] = len(r.get_day_trades(account=config["robinhood"]["account_number"])["equity_day_trades"])
trades["rh_ira"]["daytrades"] = len(r.get_day_trades(account=config["robinhood"]["ira_account_number"])["equity_day_trades"])
trades["alpaca"]["daytrades"] = requests.get("https://api.alpaca.markets/v2/account", headers=headers).json()["daytrade_count"]

with open("trades.pickle", 'wb') as file:
   pickle.dump(trades, file)


old_symbols_dicts = {}

'''
##########
# Signal #
##########
'''
def signal_handler(sig, frame):
   print("\nCtrl+C detected. Exiting.")
   sys.exit(0)

'''
#########
# Email #
#########
'''
async def send_gmail(body):
   if config["gmail"]["app_password"]:
      msg = MIMEText(body)
      msg['Subject'] = "Stock Alert! " + datetime.now().strftime("%H:%M %m-%d-%Y")
      msg['From'] = config["gmail"]["sender"]
      msg['To'] = ', '.join(config["gmail"]["receiver"])
      with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
         smtp_server.login(config["gmail"]["sender"], config["gmail"]["app_password"])
         smtp_server.sendmail(config["gmail"]["sender"], config["gmail"]["receiver"], msg.as_string())
'''
#################
# Time and Date #
#################
'''
def get_last_friday():
   today = datetime.now(pytz.timezone("EST"))
   days_to_friday = (today.weekday() - 4) % 7
   last_friday = today - timedelta(days=days_to_friday)
   return last_friday.strftime('%Y-%m-%d')

def get_timestamp(h=None, m=None, specific_date=None):
   today = date.today()
   if calendar.day_name[today.weekday()] in ("Saturday", "Sunday") and specific_date is None:
      specific_date =  datetime.strptime(get_last_friday(), '%Y-%m-%d')
      specific_date = specific_date.replace(tzinfo=pytz.timezone("EST"))
   current_time = datetime.now(pytz.timezone("EST"))
   if specific_date:
      desired_time = specific_date.replace(hour=h, minute=m, second=0, microsecond=0)
   elif h is not None and m is not None:
      desired_time = current_time.replace(hour=h, minute=m, second=0, microsecond=0)
   else:
      desired_time = current_time
   #time_difference = desired_time - current_time
   #timestamp_milliseconds = int(round((current_time + time_difference).timestamp() * 1000))
   return int(round(desired_time.timestamp()) * 1000)

def get_timestamp_alpaca(h=None, m=None, specific_date=None):
   current_time = datetime.now(pytz.timezone("EST"))
   return current_time.strftime('%Y-%m-%dT%H:%M:%S-05:00')

def milliseconds_to_time_date(m):
    return datetime(1970, 1, 1) + timedelta(seconds=(m / 1000.0))

def get_prev_mins(m=5):
   new_time = datetime.now() - timedelta(minutes=m)
   rounded_time = datetime(
      new_time.year, new_time.month, new_time.day,
      new_time.hour, new_time.minute - new_time.minute % 1, 0, 0
   )
   return math.floor(rounded_time.timestamp() * 1000)

def get_prev_mins_alpaca(m):
   current_time = datetime.now(pytz.timezone("EST"))
   time_ago = current_time - timedelta(minutes=m)
   return time_ago.strftime('%Y-%m-%dT%H:%M:%S-05:00')

def get_last_trade_day_alpaca():
   current_time = datetime.now(pytz.timezone("EST"))
   if calendar.day_name[current_time.weekday()] in ("Monday"):
      time_ago = current_time - timedelta(days=3)
      return time_ago.strftime('%Y-%m-%dT%H:%M:%S-05:00')
   elif calendar.day_name[current_time.weekday()] in ("Sunday"):
      time_ago = current_time - timedelta(days=2)
      return time_ago.strftime('%Y-%m-%dT%H:%M:%S-05:00')
   elif calendar.day_name[current_time.weekday()] in ("Saturday"):
      time_ago = current_time - timedelta(days=1)
      return time_ago.strftime('%Y-%m-%dT%H:%M:%S-05:00')
   else:
      time_ago = current_time - timedelta(days=1)
      return time_ago.strftime('%Y-%m-%dT%H:%M:%S-05:00')

def get_market_hours_type():
   now = datetime.now(pytz.timezone("EST")).time()
   if datetime.strptime("4:00", "%H:%M").time() <= now < datetime.strptime("9:30", "%H:%M").time():
      return "pre"
   elif datetime.strptime("9:30", "%H:%M").time() <= now < datetime.strptime("15:00", "%H:%M").time():
      return "market"
   elif datetime.strptime("16:00", "%H:%M").time() <= now < datetime.strptime("20:00", "%H:%M").time():
      return "post"
   else:
      return None

'''
###########
# Symbols #
###########
'''
def finviz():
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

async def stockanalysis():
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
async def get_symbols():
   return await stockanalysis()

def update_symbols():
   if not os.path.exists("./previous_symbols"):
      os.makedirs("./previous_symbols")
   #dest_file = os.path.join(dest_directory, os.path.basename(src_file))
   os.rename("symbols.pickle", "./previous_symbols/symbols_" + datetime.now().strftime("%m-%d-%Y") + ".pickle")
   get_symbols()

def get_otc_status(ticker):
   headers = {
      "accept": "application/json",
      "APCA-API-KEY-ID": config["alpaca"]["api_key"],
      "APCA-API-SECRET-KEY": config["alpaca"]["secret"]
   }
   data = requests.get("https://api.alpaca.markets/v2/assets/" + ticker, headers=headers).json()
   return data["exchange"]

'''
########
# Math #
########
'''
def get_percentage(open, close):
   return ((close-open)/open)*100

#print(fibonacci_retracement(swing_high, swing_low, 23.6))
#print(fibonacci_retracement(swing_high, swing_low, 38.2))
#print(fibonacci_retracement(swing_high, swing_low, 50))
#print(fibonacci_retracement(swing_high, swing_low, 61.8))
#print(fibonacci_retracement(swing_high, swing_low, 78.6))
def fibonacci_retracement(swing_high, swing_low, retracement_percentage):
   return swing_low + (retracement_percentage / 100) * (swing_high - swing_low)

'''
###############
# Market Data #
###############
'''
def alpaca_get(ticker, f, t, l, s, tf, session=None):
   #url = "https://data.alpaca.markets/v2/stocks/bars?symbols=" + ticker + "&start=" + f + "&end=" + t + "&limit=" + l + "&feed=sip&sort=" + s + "&timeframe=" + tf
   if get_otc_status(ticker) == "otc":
      url = "https://data.alpaca.markets/v2/stocks/" + ticker + "/bars?timeframe=" + tf + "&start=" + f + "&end=" + t + "&limit=" + str(l) + "&adjustment=all&feed=otc&sort=" + s
   else:
      url = "https://data.alpaca.markets/v2/stocks/" + ticker + "/bars?timeframe=" + tf + "&start=" + f + "&end=" + t + "&limit=" + str(l) + "&adjustment=all&feed=sip&sort=" + s

   headers = {
      "APCA-API-KEY-ID": config["alpaca"]["api_key"],
      "APCA-API-SECRET-KEY": config["alpaca"]["secret"],
      "accept": "application/json"
   }

   if session:
      session.headers.update(headers)
      while True:
         try:
            response = session.get(url, timeout=1)
            if response.status_code == 200:
               return response.json()
            response.raise_for_status()
         except requests.exceptions.Timeout:
            pass
         except requests.exceptions.RequestException as e:
            pass
   else:
      while True:
         try:
            response = requests.get(url, headers=headers, timeout=1)
            if response.status_code == 200:
               return response.json()
            response.raise_for_status()
         except requests.exceptions.Timeout:
            pass
         except requests.exceptions.RequestException as e:
            pass

def get_alpaca_data(ticker, f, t, l, session=None, result_queue=None):
   #if f > t:
   #   print("Fatal: From time higher than To time!", f, t)
   c = alpaca_get(ticker, f, t, l, "asc", "1Min", session)
   if result_queue and c:
      result_queue.put((ticker, c))
   else:
      return c

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

def get_trades_alpaca(ticker):

   url = "https://data.alpaca.markets/v2/stocks/AAPL/trades/latest?feed=sip"

   headers = {
      "accept": "application/json",
      "APCA-API-KEY-ID": config["alpaca"]["api_key"],
      "APCA-API-SECRET-KEY": config["alpaca"]["secret"]
   }

   return requests.get(url, headers=headers).json()

'''
##############
# Strategies #
##############
'''
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

def get_earnings():
   headers = {"User-Agent": config["settings"]["user_agent"]["value"]}
   today = datetime.now()
   d = today.strftime('%Y-%m-%d')
   response = requests.get("https://api.nasdaq.com/api/calendar/earnings?date=" + d, headers=headers)
   e = response.json()
   for i in e["data"]["rows"]:
      print(d, "\033[92m", i["symbol"], '\033[0m', i["lastYearEPS"], i["epsForecast"])

'''
########
# News #
########
'''
def get_stocknewsapi(ticker):
   response = requests.get("https://stocknewsapi.com/api/v1?tickers=" + ticker + "&items=10&cache=false&page=1&&token=" + config["stocknewsapi"]["api_key"])
   n = response.json()
   a = []
   i = 0
   while i < len(n["data"]):
      d = int(datetime.strptime(n["data"][i]["date"], "%a, %d %b %Y %H:%M:%S %z").timestamp() * 1000)
      if "PressRelease" in n["data"][i]["topics"]:
         a.append((d, n["data"][i]["title"]))
      i += 1
   return a

def get_news(ticker):
   a = []
   a += get_stocknewsapi(ticker)
   return a

def parse_news(ticker):
   a = sorted(get_news(ticker), reverse=True)
   #sorted_array = sorted(a, key=lambda x: x[0], reverse=True)
   if a:
      if get_prev_mins(3) <= a[0][0]:
         print("Breaking News:", milliseconds_to_time_date(a[0][0]), a[0][1])
         asyncio.run(watch(ticker))

   i = 0
   while i < len(a):
      for keyword in config["settings"]["news_good"]["value"]:
         if any(word.lower() == keyword.lower() for word in a[i][1].split()):
            print("Previous News:", "Keyword:", keyword, milliseconds_to_time_date(a[i][0]), a[i][1])
      i += 1

'''
###########
# Trading #
###########
'''
# This assumes you are using a margin account.
async def buy_alpaca(ticker, price, q=None):
   global trades
   headers = {
      "accept": "application/json",
      "APCA-API-KEY-ID": config["alpaca"]["api_key"],
      "APCA-API-SECRET-KEY": config["alpaca"]["secret"]
   }

   if ticker in trades["alpaca"]:
      special = True
   else:
      special = False

   trades["alpaca"][ticker] = {}

   account = requests.get("https://api.alpaca.markets/v2/account", headers=headers).json()
   bp = float(account["cash"])
   if bp > float(config["settings"]["wager_bp"]["value"]):
      bp = float(config["settings"]["wager_bp"]["value"])

   ob = r.get_pricebook_by_symbol(ticker)
   price = ob["asks"][1]["price"]["amount"]

   if q:
      shares = q
   else:
      shares = math.floor(bp * float(config["settings"]["wager_percent"]["value"])/float(price))

   if trades["alpaca"][ticker].get("shares"):
      trades["alpaca"][ticker]["shares"] += shares
   else:
      trades["alpaca"][ticker]["shares"] = shares

   if account["daytrade_count"] < 3 and trades["alpaca"]["daytrades"] < 3:
      headers = {
         "accept": "application/json",
         "content-type": "application/json",
         "APCA-API-KEY-ID": config["alpaca"]["api_key"],
         "APCA-API-SECRET-KEY": config["alpaca"]["secret"]
      }
      if get_market_hours_type() == "market":
         payload = {
            "side": "buy",
            "type": "market",
            "time_in_force": "day",
            "qty": str(shares),
            "symbol": ticker
         }
         # if not day trading
         if not special:
            trades["alpaca"]["daytrades"] += 1
         print("BUYING MARKET ORDER", ticker, shares, price)
         response = requests.post("https://api.alpaca.markets/v2/orders", json=payload, headers=headers)
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
         # if not day trading
         if not special:
            trades["alpaca"]["daytrades"] += 1
         print("BUYING LIMIT ORDER", ticker, shares, price)
         response = requests.post("https://api.alpaca.markets/v2/orders", json=payload, headers=headers)

         print(response.text)


async def buy_rh_roth_ira(ticker, price, q=None):
   global trades
   if ticker in trades["rh_ira"]:
      special = True
   else:
      special = False

   trades["rh_ira"][ticker] = {}

   account = r.load_account_profile(account_number=config["robinhood"]["ira_account_number"])
   bp = float(account["buying_power"])
   if bp > float(config["settings"]["wager_bp"]["value"]):
      bp = float(config["settings"]["wager_bp"]["value"])

   ob = r.get_pricebook_by_symbol(ticker)
   price = ob["asks"][1]["price"]["amount"]

   if q:
      shares = q
   else:
      shares = math.floor(bp * float(config["settings"]["wager_percent"]["value"])/float(price))

   if trades["rh_ira"][ticker].get("shares"):
      trades["rh_ira"][ticker]["shares"] += shares
   else:
      trades["rh_ira"][ticker]["shares"] = shares

   if account["type"] == "margin":
       if float(account["portfolio_cash"]) < 25000:
          daytrades = r.get_day_trades(account=config["robinhood"]["ira_account_number"])
          if len(daytrades["equity_day_trades"]) < 3 and trades["rh_ira"]["daytrades"] < 3 and not daytrades["option_day_trades"]:
             if get_market_hours_type() == "market":
                if not special:
                   trades["rh_ira"]["daytrades"] += 1
                data = r.order_buy_market(symbol=ticker, quantity=shares, account_number=config["robinhood"]["ira_account_number"])
                print("BUYING MARKET ORDER", ticker, shares, price)
             else:
                if not special:
                   trades["rh_ira"]["daytrades"] += 1
                print("BUYING LIMIT ORDER", ticker, shares, price)
                data = r.order_buy_limit(symbol=ticker, quantity=shares, limitPrice=float(price), account_number=config["robinhood"]["ira_account_number"], extendedHours=True)

   elif account["type"] == "cash":
      if get_market_hours_type() == "market":
         r.order_buy_market(ticker, shares, account_number=config["robinhood"]["ira_account_number"])
         print("BUYING MARKET ORDER", ticker, str(shares), str(price))
      else:
         ob = r.get_pricebook_by_symbol(ticker)
         price = ob["asks"][1]["price"]["amount"]
         r.order_buy_limit(ticker, shares, float(price), account_number=config["robinhood"]["ira_account_number"], extendedHours=True)
         print("BUYING LIMIT ORDER", ticker, str(shares), str(price))

async def buy_rh(ticker, price, q=None):
   global trades
   if ticker in trades["rh"]:
      special = True
   else:
      special = False

   trades["rh"][ticker] = {}

   account = r.load_account_profile(account_number=config["robinhood"]["account_number"])
   bp = float(account["buying_power"])
   if bp > float(config["settings"]["wager_bp"]["value"]):
      bp = float(config["settings"]["wager_bp"]["value"])

   ob = r.get_pricebook_by_symbol(ticker)
   price = ob["asks"][1]["price"]["amount"]

   if q:
      shares = q
   else:
      shares = math.floor(bp * float(config["settings"]["wager_percent"]["value"])/float(price))

   if trades["rh"][ticker].get("shares"):
      trades["rh"][ticker]["shares"] += shares
   else:
      trades["rh"][ticker]["shares"] = shares

   if account["type"] == "margin":
       if float(account["portfolio_cash"]) < 25000:
          daytrades = r.get_day_trades(account=config["robinhood"]["account_number"])
          if len(daytrades["equity_day_trades"]) < 3 and trades["rh"]["daytrades"] < 3 and not daytrades["option_day_trades"]:
             if get_market_hours_type() == "market":
                if not special:
                   trades["rh"]["daytrades"] += 1
                data = r.order_buy_market(symbol=ticker, quantity=shares, account_number=config["robinhood"]["account_number"])
                print("BUYING MARKET ORDER", ticker, shares, price)
             else:
                if not special:
                   trades["rh"]["daytrades"] += 1
                print("BUYING LIMIT ORDER", ticker, shares, price)
                data = r.order_buy_limit(symbol=ticker, quantity=shares, limitPrice=float(price), account_number=config["robinhood"]["account_number"], extendedHours=True)

   elif account["type"] == "cash":
      if get_market_hours_type() == "market":
         r.order_buy_market(ticker, shares, account_number=config["robinhood"]["account_number"])
         print("BUYING MARKET ORDER", ticker, str(shares), str(price))
      else:
         ob = r.get_pricebook_by_symbol(ticker)
         price = ob["asks"][1]["price"]["amount"]
         r.order_buy_limit(ticker, shares, float(price), account_number=config["robinhood"]["account_number"], extendedHours=True)
         print("BUYING LIMIT ORDER", ticker, str(shares), str(price))


async def go_long(ticker, price, q=None):
   global trades
   with open("trades.pickle", 'rb') as file:
      trades = pickle.load(file)

   if get_market_hours_type() == "pre":
      if trades["rh"]["daytrades"] < 3:
         await buy_rh(ticker, round(price, 4), q)
         await send_gmail("Buying On Robin Hood. Ticker: " + ticker + " Price: " + str(price))
      elif trades["rh_ira"]["daytrades"] < 3:
         await buy_rh_roth_ira(ticker, round(price, 4), q)
         await send_gmail("Buying On Robin Hood IRA. Ticker: " + ticker + " Price: " + str(price))
      elif trades["alpaca"]["daytrades"] < 3:
         await buy_alpaca(ticker, round(price, 4), q)
         await send_gmail("Buying Alpaca. Ticker: " + ticker + " Price: " + str(price))

      with open("trades.pickle", 'wb') as file:
         pickle.dump(trades, file)

async def sell_rh(ticker, price, q=None):
   global trades
   if q:
      shares = int(q)
   elif trades["rh"][ticker].get("shares"):
      shares = int(trades["rh"][ticker]["shares"])
   else:
      return

   if get_market_hours_type() == "market":
      r.order_sell_market(symbol=ticker, quantity=shares, account_number=config["robinhood"]["account_number"])
      print("robinhood: Selling Market Order", ticker, shares, str(price))
   else:
      wob = r.get_pricebook_by_symbol(ticker)
      price = ob["bids"][1]["price"]["amount"]
      r.order_sell_limit(ticker, shares, float(price), account_number=config["robinhood"]["account_number"], extendedHours=True)
      print("robinhood: Selling Limit Order", ticker, str(shares), str(price))

   del trades["rh_ira"][ticker]

async def sell_rh_roth_ira(ticker, price, q=None):
   global trades
   if q:
      shares = int(q)
   elif trades["rh_ira"][ticker].get("shares"):
      shares = int(trades["rh_ira"][ticker]["shares"])
   else:
      return

   if get_market_hours_type() == "market":
      r.order_sell_market(symbol=ticker, quantity=shares, account_number=config["robinhood"]["ira_account_number"])
      print("robinhood ira: Selling Market Order", ticker, shares, str(price))
   else:
      ob = r.get_pricebook_by_symbol(ticker)
      price = ob["bids"][1]["price"]["amount"]
      r.order_sell_limit(ticker, shares, float(price), account_number=config["robinhood"]["ira_account_number"], extendedHours=True)
      print("robinhood ira: Selling Limit Order", ticker, str(shares), str(price))

   del trades["rh_ira"][ticker]


async def sell_alpaca(ticker, price, q=None):
   global trades
   headers = {
      "accept": "application/json",
      "content-type": "application/json",
      "APCA-API-KEY-ID": config["alpaca"]["api_key"],
      "APCA-API-SECRET-KEY": config["alpaca"]["secret"]
   }

   if q:
      shares = q
   elif trades["alpaca"][ticker].get("shares"):
      shares = trades["alpaca"][ticker]["shares"]
   else:
      return

   if get_market_hours_type() == "market":
      payload = {
         "side": "sell",
         "type": "market",
         "time_in_force": "day",
         "qty": str(shares),
         "symbol": ticker
      }
      response = requests.post("https://api.alpaca.markets/v2/orders", json=payload, headers=headers)
      print("alpaca: Selling Market Order", ticker, shares, str(price))
   else:
      ob = r.get_pricebook_by_symbol(ticker)
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
      response = requests.post("https://api.alpaca.markets/v2/orders", json=payload, headers=headers)
      print("alpaca: Selling Limit Order", ticker, str(shares), str(price))

   del trades["alpaca"][ticker]

async def sell(ticker, price, q=None):
   global trades
   with open("trades.pickle", 'rb') as file:
      trades = pickle.load(file)

   if ticker in trades["rh_ira"]:
      await sell_rh_roth_ira(ticker, round(price, 4), q)
      await send_gmail("Selling On Robin Hood Roth IRA. Ticker: " + ticker + " Price: " + str(price))
   if ticker in trades["rh"]:
      await sell_rh(ticker, round(price, 4), q)
      await send_gmail("Selling On Robin Hood. Ticker: " + ticker + " Price: " + str(price))
   elif ticker in trades["alpaca"]:
      await sell_alpaca(ticker, round(price, 4), q)
      await send_gmail("Selling On Alpaca. Ticker: " + ticker + " Price: " + str(price))

   with open("trades.pickle", 'wb') as file:
      pickle.dump(trades, file)

def go_short(ticker):
   print("stub")

def watch_start(ticker):
   #asyncio.run(watch_polygon(subs, ticker))
   asyncio.run(watch_alpaca(ticker))

# fcl = first candle low
#async def trade(ticker, price, broker, fcl):


#
#   #if get_market_hours_type() == "pre":
#      # if the price of the stock goes below 7 percent of the low of the first movement candle
#
#      #if price <= (c["bars"][-1]["l"] - (c["bars"][-1]["l"] *.07)):
#      #   await sell(ticker, price)
#      #   return True
#      # if a great move happened in 5 minutes sell, [RVSN 1/22/24 148%]
#      if get_percentage(trades[broker][ticker]["low"], trades[broker][ticker]["high"]) > 40:
#         if price <= target_sell:
#            await sell(ticker, price)
#            return True
#   elif get_market_hours_type() == "market" or get_market_hours_type() == "post":
#      if price <= target_sell:
#         print(ticker, "Target Sell", target_sell)
#         await sell(ticker, price)
#         return True
#
   return False

async def watch_alpaca(ticker):
   global trades
   p = 0
   to = 0
   # This is a race condition when called multiple times
   if trades["rh"]["daytrades"] < 3:
      broker = "rh"
   elif trades["rh_ira"]["daytrades"] < 3:
      broker = "rh_ira"
   elif trades["alpaca"]["daytrades"] < 3:
      broker = "alpaca"
   else:
      return

   #if not ticker in trades[broker]:
   trades[broker][ticker] = {}
   trades[broker][ticker]["high"] = 0
   trades[broker][ticker]["low"] = sys.maxsize

   now = datetime.now(pytz.timezone("EST")).time()
   c = get_alpaca_data(ticker, get_prev_mins_alpaca(15), get_timestamp_alpaca(now.hour, now.minute), 15)
   if c.get("bars"):
      if len(c["bars"]) == 1:
         lc = get_alpaca_data(ticker, get_last_trade_day_alpaca(), get_timestamp_alpaca(now.hour, now.minute), 2000)
         c["bars"] = lc["bars"] + c["bars"]
   else:
      c = get_alpaca_data(ticker, get_last_trade_day_alpaca(), get_timestamp_alpaca(now.hour, now.minute), 2000)

   i = 0
   for item in reversed(c["bars"]):
      if i >= 15:
         break
      if item["l"] < trades[broker][ticker]["low"]:
         trades[broker][ticker]["low"] = item["l"]
         print("LOW:", ticker, trades[broker][ticker]["low"])
      if item["h"] > trades[broker][ticker]["high"]:
         trades[broker][ticker]["high"] = item["h"]
      i += 1
      fcl = trades[broker][ticker]["low"]

#
#   while i < len(c["bars"]):
#      if i >= 15:
#         break
#      if c["bars"][i]["l"] < trades[broker][ticker]["low"]:
#         trades[broker][ticker]["low"] = c["bars"][i]["l"]
#      if c["bars"][i]["h"] > trades[broker][ticker]["high"]:
#         trades[broker][ticker]["high"] = c["bars"][i]["h"]
#      i += 1

   ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
   ssl_context.load_verify_locations(certifi.where())
   sub = False
   async for s in connect("wss://stream.data.alpaca.markets/v2/sip", close_timeout=5, ssl=ssl_context):
      try:
         cmsg = await s.recv()
         #print(cmsg)
         await s.send(json.dumps({"action": "auth", "key": config["alpaca"]["api_key"], "secret": config["alpaca"]["secret"]}))
         amsg = await s.recv()
         #print(amsg)
         while True:
            if not sub:
               if type(ticker) == list:
                  await s.send(json.dumps({"action": "subscribe", "trades": ticker}))
               else:
                  await s.send(json.dumps({"action": "subscribe", "trades": ticker.split()}))
               try:
                  sub_msg = await asyncio.wait_for(s.recv(), timeout=3)
                  print(sub_msg)
                  sub = True
               except asyncio.TimeoutError:
                  sub = False
                  continue
            try:
               msgr = await asyncio.wait_for(s.recv(), timeout=7)
               msg = json.loads(msgr)
            except asyncio.TimeoutError:
               print(ticker, "No stock movement detected after 7 seconds.")
               await s.close()
               return
               to += 1
               if to >= 60*4:
                  await s.close()
                  return
               continue

            for m in msg:
               if m["T"] == "error":
                  if "auth timeout" in m["msg"]:
                     await s.send(json.dumps({"action": "auth", "key": config["alpaca"]["api_key"], "secret": config["alpaca"]["secret"]}))
                     auth_msg = await s.recv()
                     sub = False
                     continue
                  else:
                     print("MSG:", m)


               if not p and m["T"] != "error":
                  print(ticker)
                  if m["p"] >= 1.08 * trades[broker][ticker].get("low"):
                     await go_long(ticker, m["p"])
                     p = 1

               if p:
                 if price > trades[broker][ticker]["high"]:
                    trades[broker][ticker]["high"] = price
                    print(ticker, "High", trades[broker][ticker]["high"])
                 if price < trades[broker][ticker]["low"]:
                    trades[broker][ticker]["low"] = price
                    print(ticker, "Low", trades[broker][ticker]["low"])

                 target_sell = fibonacci_retracement(trades[broker][ticker]["low"], trades[broker][ticker]["high"], 23.6)
                 print("Target Sell:", ticker, target_sell)
                 if m["p"] <= target_sell:
                    await sell(ticker, m["p"])
                    await s.close()
                    return
                 if m["p"] <= (fcl - (fcl *.07)):
                    await sell(ticker, m["p"])
                    await s.close()
                    return

      except ConnectionClosedOK as e:
         return
      except ConnectionClosedError as e:
         sub = True
         continue

'''
#############
# Processes #
#############
'''
def start_scan():
   symbols = get_symbols()
   global old_symbols_dicts
   symbols_dicts = {}
   with requests.Session() as session:
      with multiprocessing.Manager() as manager:
         result_queue = manager.Queue()
         with multiprocessing.Pool(processes=multiprocessing.cpu_count() * int(config["settings"]["multiplier"]["value"])) as pool:
            pool.starmap(scan_current_move_poly, [(symbols[i], result_queue, session) for i in range(len(symbols))])

         try:
            while True:
               if not result_queue.empty():
                  symbols_dicts.update(result_queue.get_nowait())
               else:
                  break
         except Exception as e:
            print(f"An error occurred: {e}")
#      for results in enumerate(symbols_dicts):
#         print(results)
   if symbols_dicts:
      if old_symbols_dicts != symbols_dicts:
         old_symbols_dicts = symbols_dicts
         for ticker in symbols_dicts:
            if not ticker:
               print("SYMBOLS_DICTS:", symbols_dicts)
            else:
               print("TICKER:", "\033[92m", ticker, "\033[0m")
               parse_news(ticker)
   return symbols_dicts

def run_stream():
   subprocess.run("/home/archer/stream2.sh")

def stop_stream():
   subprocess.run(["killall", "/home/archer/stream2.sh"])

'''
############
# Charting #
############
'''
async def client_chart():
   async with websockets.connect('ws://localhost:8765') as websocket:
    a = 1
    while a:
       data = await websocket.recv()
       ticker, serialized_data = json.loads(data)
       candles = [Candle(*candle) for candle in serialized_data]
       chart = Chart(candles)
       chart.set_name(ticker)
       chart.set_volume_pane_height(6)
       chart.set_volume_pane_enabled(True)
       chart.draw()

async def server():
   print("Server process started")
   async with websockets.serve(handler, "localhost", 8765):
      await asyncio.Future()  # Serve indefinitely

def main():
   #old_d = {}
   #get_symbols()
   signal.signal(signal.SIGINT, signal_handler)
   #schedule.every().day.at("00:00").do(update_symbols)
   #schedule.every().day.at("02:00").do(run_stream)
   #schedule.every().day.at("20:00").do(stop_stream)
   scheduler = AsyncIOScheduler()
   news = StockNewsAPI()
   scheduler.add_job(news.get_all_stocknewsapi, trigger=CronTrigger(second=2, minute='*', hour='7-17', day_of_week='mon-fri', timezone=pytz.timezone('US/Eastern')))
   scheduler.start()
   asyncio.get_event_loop().run_forever()
   try:
      while True:
         next
#         #schedule.run_pending()
#         today = date.today()
#         if calendar.day_name[today.weekday()] in ("Saturday", "Sunday"):
#            t.sleep(60)
#         else:
#            if time(4, 0) <= datetime.now(pytz.timezone("EST")).time() < time(20, 0):
#               d = start_scan()
#               if d:
#                  #if not old_d:
#                  #   old_d = d
#                  #   print(d)
#                  if old_d != d:
#                     old_d = d
#                     print(d)
#               #else:
#               #   print(d)

   except SystemExit:
      pass

if __name__ == "__main__":
   args = sys.argv
   if len(args) > 1:
      get_earnings()
      if "earnings" in args:
         schedule.every().day.at("05:00").do(get_earnings)
         while True:
            schedule.run_pending()
            t.sleep(60)

      if "chart" in args:
         asyncio.get_event_loop().run_until_complete(client_chart())

   else:
      main()

#async def server():
#    print("Server process started")
#    async with websockets.serve(handler, "localhost", 8765):
#        await asyncio.Future()  # Serve indefinitely
#
#async def handler(websocket, path):
#    print("Connection established with client")
#    try:
#        for ticker, candles in candle_data.items():
#            # Serialize the candle data
#            serialized_data = [[candle.open, candle.close, candle.high, candle.low] for candle in candles]
#
#            # Send the serialized data to the client
#            await websocket.send(json.dumps((ticker, serialized_data)))
#    except Exception as e:
#        print(f"Error sending candle data: {e}")
#
#def run_server():
#    asyncio.run(server())
#
#async def server(websocket, path):
#    print("Connection established with client")
#    try:
#        for ticker, candles in candle_data.items():
#            # Serialize the candle data
#            serialized_data = [[candle.open, candle.close, candle.high, candle.low] for candle in candles]
#
#            # Send the serialized data to the client
#            await websocket.send(json.dumps((ticker, serialized_data)))
#    except Exception as e:
#        print(f"Error sending candle data: {e}")
#
#start_server = websockets.serve(server, "localhost", 8765)
#
#asyncio.get_event_loop().run_until_complete(start_server)
#asyncio.get_event_loop().run_forever()
