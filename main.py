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

#sell call
# topping tail that is red followed by a red candle
#sell put/buy call
# bottoming tail followed by a green candle
#set break points and invisible stop point
#previous low on previous candle if it goes below, reversal


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

from sequoia import sequoia

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
r = Robinhood(config["robinhood"]["user"], config["robinhood"]["password"], device_token=config["robinhood"]["device_token"])
def signal_handler(sig, frame):
   print("\nCtrl+C detected. Exiting.")
   sys.exit(0)

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
   try:
      while True:
         next
         #schedule.run_pending()
         today = date.today()
         if calendar.day_name[today.weekday()] in ("Saturday", "Sunday"):
            t.sleep(60)
         else:
            if time(4, 0) <= datetime.now(pytz.timezone("EST")).time() < time(20, 0):
               #d = start_scan()
               d = Sequoia.tasks.scan_small_cap()
               if d:
                  #if not old_d:
                  #   old_d = d
                  #   print(d)
                  if old_d != d:
                     old_d = d
                     print(d)
               #else:
               #   print(d)

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
