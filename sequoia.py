#
#
#import asyncio, calendar, certifi, json, math, multiprocessing, os, pickle, pytz, re, requests, signal, schedule, smtplib, socket, ssl, sys, websockets
##import robin_stocks.robinhood as r
#import time as t
#from apscheduler.schedulers.asyncio import AsyncIOScheduler
#from apscheduler.triggers.cron import CronTrigger
#from candlestick_chart import Candle, Chart
#from datetime import datetime, date, timedelta, time, timezone
#from lxml import html
#from uuid import uuid4
#from websockets.client import connect, WebSocketClientProtocol
#from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError
#
#from sequoia import sequoia
#
## Limit to get polygon data based on how many minutes there is in the market hours type
#PRE_LIMIT = 350*4
#MARKET_LIMIT = 400*4
#POST_LIMIT = 250*4
#
## Time when each market type starts for hours and minutes
##PRE_H = 4
##PRE_M = 0
##MARKET_H = 9
##MARKET_M = 30
##POST_H = 16
##POST_M = 0
##CLOSE_H = 20
##CLOSE_M = 0
#with open("config.json", "r") as jsonfile: config = json.load(jsonfile)
#def signal_handler(sig, frame):
#   print("\nCtrl+C detected. Exiting.")
#   sys.exit(0)
#if __name__ == "__main__":
#   signal.signal(signal.SIGINT, signal_handler)
#   args = sys.argv
##   if len(args) > 1:
##      if "swing" in args:
##      if "chart" in args:
##   except SystemExit:
##      pass
#
##


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

#sell call
# topping tail that is red followed by a red candle
#sell put/buy call
# bottoming tail followed by a green candle
#set break points and invisible stop point
#previous low on previous candle if it goes below, reversal




# Usage: from Sequoia import Sequoia

import asyncio, calendar, json, schedule, threading, pytz

import time as t

from flask import Flask, request
from concurrent.futures import ThreadPoolExecutor

from datetime import datetime, date, timedelta, time, timezone


import endpoints, apps, tools

class Sequoia():

   def __init__(self, confile):
      #self.old_symbols_dicts = {}
      #self.trades = {}

      with open(confile, "r") as jsonfile: self.config = json.load(jsonfile)

      self.robinhood = endpoints.Robinhood(self.config["robinhood"]["user"],
                                           self.config["robinhood"]["password"],
                                           self.config["robinhood"]["device_token"],
                                           self.config["settings"]["user_agent"]["value"]
                                          )

      self.alpaca = endpoints.Alpaca(self.config["alpaca"]["api_key"],
                                     self.config["alpaca"]["secret"],
                                    )

      #self.polygon = endpoints.Polygon(self.config

      #self.snapi = endpoints.StockNewsAPI(self.config["stocknewsapi"]["api_key"])

      #self.stocks = api.stocks(self.robinhood, self.alpaca)
      #self.options = api.options(self.robinhood, self.alpaca)

      self.tools = tools

      #self.api = api

      self.apps = apps

      self._flask = Flask(__name__)

      # Define routes
      self._setup_routes()

   def _setup_routes(self):
      # Pass the required route to the decorator
      @self._flask.route("/hello")
      def hello():
          return "Hello, Welcome to GeeksForGeeks"

      @self._flask.route("/greet")
      def greet():
          name = request.args.get('name', 'Guest')  # Default to 'Guest' if 'name' is not provided
          return f"Hello, {name}!"

      @self._flask.route("/")
      def index():
          index = "<a href=/greet>Greet</a>"
          return index
      @self._flask.route('/action', methods=['POST'])
      def handle_action():
          data = request.json
          action = data.get('action')
          if action == 'get_variable':
              return jsonify(variable=self.my_variable)
          elif action == 'set_variable':
              new_value = data.get('value')
              if new_value:
                  self.my_variable = new_value
                  return jsonify(message="Variable updated successfully")
              else:
                  return jsonify(message="No value provided"), 400
          elif action == 'greet':
              return jsonify(message="Hello!")
          elif action == 'farewell':
              return jsonify(message="Goodbye!")
          else:
              return jsonify(message=f"Unknown action: {action}"), 400

   def _flaskrun(self):
      self._flask.run(port=5000, use_reloader=False)  # use_reloader=False to prevent reloading in threaded mode

   def start(self):
      #schedule.every().day.at("00:00").do(self.tools.get_symbols)
      #schedule.every().day.at("05:00").do(self.tools.get_earnings)

      flask_thread = threading.Thread(target=self._flaskrun)
      flask_thread.daemon = True  # Daemonize thread so it exits when the main program does
      flask_thread.start()


      app1 = self.apps.TurboOptionScalper(self.robinhood)
      app1_thread = threading.Thread(target=app1.main)
      app1_thread.daemon = True  # Daemonize thread so it exits when the main program does
      app1_thread.start()

      while True:
         schedule.run_pending()
         today = date.today()
         if calendar.day_name[today.weekday()] in ("Saturday", "Sunday"):
            t.sleep(60)
         else:
            if time(4, 0) <= datetime.now(pytz.timezone("EST")).time() < time(20, 0):
               #d = self.tasks.scan_small_cap()
               #d = self.tasks.scan_small_cap()
               d = 0
               if d:
                  if old_d != d:
                     old_d = d
                     print(d)

   # fcl = first candle low
   #async def trade(ticker, price, broker, fcl):

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
#      return False




