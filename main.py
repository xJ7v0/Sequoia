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

if __name__ == "__main__":
   signal.signal(signal.SIGINT, signal_handler)
   args = sys.argv
   if len(args) > 1:
      if "swing" in args:

      if "chart" in args:
         asyncio.get_event_loop().run_until_complete(client_chart())


#   except SystemExit:
#      pass

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
