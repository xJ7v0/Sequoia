

'''
Displays a chart
'''
#class chart:
#
#   async def server(self):
#      print("Server process started")
#      async with websockets.serve(handler, "localhost", 8765):
#         await asyncio.Future()  # Serve indefinitely
#
##async def handler(websocket, path):
##    print("Connection established with client")
##    try:
##        for ticker, candles in candle_data.items():
##            # Serialize the candle data
##            serialized_data = [[candle.open, candle.close, candle.high, candle.low] for candle in candles]
##
##            # Send the serialized data to the client
##            await websocket.send(json.dumps((ticker, serialized_data)))
##    except Exception as e:
##        print(f"Error sending candle data: {e}")
##
#
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
#
#
#   async def client(self):
#      async with websockets.connect('ws://localhost:8765') as websocket:
#       a = 1
#       while a:
#          data = await websocket.recv()
#          ticker, serialized_data = json.loads(data)
#          candles = [Candle(*candle) for candle in serialized_data]
#          chart = Chart(candles)
#          chart.set_name(ticker)
#          chart.set_volume_pane_height(6)
#          chart.set_volume_pane_enabled(True)
#          chart.draw()
#
#
#   def main():
#      #print("Need server")
#      #asyncio.run(self.server())
#      #asyncio.get_event_loop().run_until_complete(client_chart())
#      #client()
#start_server = websockets.serve(server, "localhost", 8765)
#
#asyncio.get_event_loop().run_until_complete(start_server)
#asyncio.get_event_loop().run_forever()
#
#async def server():
#
#

#
#
#   async def watch_polygon(subs, ticker):
#      p = 0
#      if trades["rh_ira"]["daytrades"] < 3:
#         broker = "rh_ira"
#      elif trades["alpaca"]["daytrades"] < 3:
#         broker = "alpaca"
#
#      if not ticker in trades[broker]:
#         trades[broker][ticker] = {}
#
#      trades[broker][ticker]["high"] = 0
#      trades[broker][ticker]["low"] = sys.maxsize
#      now = datetime.now(pytz.timezone("EST")).time()
#      c = get_poly_data(ticker, get_prev_mins(15), get_timestamp(now.hour, now.minute), 60)
#      length = 0
#      if c:
#         i = 0
#         while i < c["resultsCount"]:
#            if c["results"][i]["l"] < trades[broker][ticker]["low"]:
#               trades[broker][ticker]["low"] = c["results"][i]["l"]
#            if c["results"][i]["h"] > trades[broker][ticker]["high"]:
#               trades[broker][ticker]["high"] = c["results"][i]["h"]
#            #candles += [Candle(open=c["results"][i]["o"], close=c["results"][i]["c"], high=c["results"][i]["h"], low=c["results"][i]["l"], volume=c["results"][i]["v"])]
#            i += 1
#
#   #      try:
#   #         for t, c in candles.items():
#   #            # Serialize the candle data
#   #            #serialized_data = [(candle.open, candle.close, candle.high, candle.low) for candle in candles]
#   #            serialized_data = [[candle.open, candle.close, candle.high, candle.low, camdle.volume] for candle in c]
#   #            await websocket.send(json.dumps((ticker, serialized_data)))
#   #      except Exception as e:
#   #         pass
#   #asyncio.get_event_loop().run_until_complete(client())
#
#      ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
#      ssl_context.load_verify_locations(certifi.where())
#      sub = True
#      async for s in connect("wss://socket.polygon.io/stocks", close_timeout=1, ssl=ssl_context):
#         try:
#            cmsg = await s.recv()
#            await s.send(json.dumps({"action": "auth", "params": config["polygon"]["api_key"]}))
#            auth_msg = await s.recv()
#            while True:
#               if sub:
#                  await s.send(json.dumps({"action": "subscribe", "params": "T." + ticker}))
#                  #await s.send(json.dumps({"action": "subscribe", "params": ",".join(subs)}))
#                  #smsg = await asyncio.wait_for(s.recv(), timeout=3)
#                  try:
#                     smsg = await asyncio.wait_for(s.recv(), timeout=3)
#                     sub = False
#                  except asyncio.TimeoutError:
#                     sub = True
#                     continue
#               try:
#                  msgr = await asyncio.wait_for(s.recv(), timeout=7)
#                  msg = json.loads(msgr)
#               except asyncio.TimeoutError:
#                  print(ticker, "No stock movement detected after 7 seconds.")
#                  await s.close()
#                  return
#               if msg[0]["ev"] == "status":
#                  if msg[0]["status"] == "max_connections":
#                     print("Max Connections exceeded")
#                     await s.close()
#                     return
#
#               length += len(msg)
#               for m in msg:
#                  if not p:
#                     if length > 3:
#                        await go_long(ticker, m["p"])
#                        p = 1
#
#                  if trade(ticker, m["p"]) == True:
#                     await s.close()
#                     return
#
#         except ConnectionClosedOK as e:
#            return
#         except ConnectionClosedError as e:
#            sub = True
#            continue
#
