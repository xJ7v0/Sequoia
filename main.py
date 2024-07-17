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



# first price to make a new high
# if price > previous red candle open; then buy
# if price < previous green candle ;then sell

# if doji then reversal
#find_channel()
import asyncio, calendar, certifi, json, math, multiprocessing, os, pickle, pytz, re, requests, signal, schedule, smtplib, socket, ssl, sys, websockets
#import robin_stocks.robinhood as r
import time as t
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from candlestick_chart import Candle, Chart
from datetime import datetime, date, timedelta, time, timezone
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

#"alpaca": {"daytrades": 0}, "ibkr": {"daytrades": 0}, "ibkr_ira": {"daytrades": 0}}
#trades["alpaca"]["daytrades"] = requests.get("https://api.alpaca.markets/v2/account", headers=headers).json()["daytrade_count"]

with open("trades.pickle", 'wb') as file:
   pickle.dump(trades, file)


'''
##########
# Signal #
##########
'''
def signal_handler(sig, frame):
   print("\nCtrl+C detected. Exiting.")
   sys.exit(0)

'''
#################
# Time and Date #
#################
'''

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
   #if get_otc_status(ticker) == "otc":
   #   url = "https://data.alpaca.markets/v2/stocks/" + ticker + "/bars?timeframe=" + tf + "&start=" + f + "&end=" + t + "&limit=" + str(l) + "&adjustment=all&feed=otc&sort=" + s
   #else:
   url = "https://data.alpaca.markets/v2/stocks/" + ticker + "/bars?timeframe=" + tf + "&start=" + f + "&end=" + t + "&limit=" + str(l) + "&adjustment=all&feed=sip&sort=" + s

   if session:
      headers = {
         "APCA-API-KEY-ID": config["alpaca"]["api_key"],
         "APCA-API-SECRET-KEY": config["alpaca"]["secret"],
         "accept": "application/json",
         "Connection": "keep-alive"
      }

   else:
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
#sell call
# topping tail that is red followed by a red candle
#sell put/buy call
# bottoming tail followed by a green candle
#set break points and invisible stop point
#previous low on previous candle if it goes below, reversal



async def scan_swing():
   symbols = await get_symbols()
   session = requests.Session()
   c = {}
   good = []
   now = datetime.now(pytz.timezone("EST"))
   _from = now - timedelta(days=7)
   t = get_timestamp_alpaca()
   for ticker in symbols:
      c = alpaca_get(ticker, _from.strftime('%Y-%m-%dT%H:%M:%S-05:00'), t, 30, "asc", "1Day", session)
      i = 0
      if c.get("bars") is not None:
         #print(c["bars"])
         while i < len(c["bars"]):
            if get_percentage(c["bars"][i]["o"], c["bars"][i]["c"]) > 10:
               print(ticker)
               good += [ticker]
            i += 1

   with open('swing.pickle', 'wb') as f:
      pickle.dump(good, f)


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
async def scalp_spy():
   account = r.load_account_profile(account_number=config["robinhood"]["ira_account_number"])
   bp = float(account["buying_power"])

   chains = r.get_option_chains("SPY")
   #price = ob["asks"][1]["price"]["amount"]



   if q:
      shares = q
   else:
      shares = math.floor(bp * float(config["settings"]["wager_percent"]["value"])/float(price))


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




async def go_long(ticker, price, q=None):
   global trades
   with open("trades.pickle", 'rb') as file:
      trades = pickle.load(file)

   if get_market_hours_type() == "pre":
      if trades["rh"]["daytrades"] < 3:
         await buy_rh(ticker, round(price, 4), q)
         await send_gmail("Buying On Robin Hood. Ticker: " + ticker + " Price: " + str(price))
      #elif trades["rh_ira"]["daytrades"] < 3:
      #   await buy_rh_roth_ira(ticker, round(price, 4), q)
      #   await send_gmail("Buying On Robin Hood IRA. Ticker: " + ticker + " Price: " + str(price))
      #elif trades["alpaca"]["daytrades"] < 3:
      #   await buy_alpaca(ticker, round(price, 4), q)
      #   await send_gmail("Buying Alpaca. Ticker: " + ticker + " Price: " + str(price))

      with open("trades.pickle", 'wb') as file:
         pickle.dump(trades, file)


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
      #get_earnings()
      if "earnings" in args:
         schedule.every().day.at("05:00").do(get_earnings)
         while True:
            schedule.run_pending()
            t.sleep(60)

      if "swing" in args:
         asyncio.run(scan_swing())

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
