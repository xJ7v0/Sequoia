#from example_module import example_module as ModuleClass

class Sequoia():
   def __init__(self):
      #self.trades = {}
      self.robinhood = Robinhood(user, pass)
      self.alpaca = alpaca(self.Robinhood)
      self.polygon = Polygon()

      self.tasks = tasks(self.alpaca, self.robinhood, self.polygon)

class tasks:
   def __init__(self, alpaca, robinhood, polygon):
      self.old_symbols_dicts = {}

   def scan_small_cap(self):
      '''
      This function uses polygon.io to scan small cap stocks with low float for movement
      '''
      symbols = tools.get_symbols()
      symbols_dicts = {}
      with multiprocessing.Manager() as manager:
         result_queue = manager.Queue()
         with multiprocessing.Pool(processes=multiprocessing.cpu_count() * int(config["settings"]["multiplier"]["value"])) as pool:
            pool.starmap(self.polygon.if_8_percent_gain, [(symbols[i], result_queue) for i in range(len(symbols))])
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
         if self.old_symbols_dicts != symbols_dicts:
            self.old_symbols_dicts = symbols_dicts
            for t in symbols_dicts:
               if not t:
                  print("SYMBOLS_DICTS:", symbols_dicts)
               else:
                  print("TICKER:", "\033[92m", t, "\033[0m")
                  parse_news(t)
      return symbols_dicts

   async def scan_swing():
      symbols = await tools.get_symbols()
      c = {}
      good = []
      now = datetime.now(pytz.timezone("EST"))
      _from = now - timedelta(days=7)
      t = get_timestamp_alpaca()
      for ticker in symbols:
         #c = alpaca_get(ticker, _from.strftime('%Y-%m-%dT%H:%M:%S-05:00'), t, 30, "asc", "1Day", session)
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

###################################################################################################
   def small_cap_news_scan():
      scheduler = AsyncIOScheduler()
      news = StockNewsAPI()
      scheduler.add_job(news.get_all_stocknewsapi, trigger=CronTrigger(second=2, minute='*', hour='7-17', day_of_week='mon-fri', timezone=pytz.timezone('US/Eastern')))
      scheduler.start()
      asyncio.get_event_loop().run_forever()


   def watch_start(ticker):
      #asyncio.run(watch_polygon(subs, ticker))
      asyncio.run(watch_alpaca(ticker))

   async def watch_alpaca(ticker):
      p = 0
      to = 0

      #if not ticker in trades[broker]:
      #trades[broker][ticker] = {}
      #trades[broker][ticker]["high"] = 0
      #trades[broker][ticker]["low"] = sys.maxsize

      now = datetime.now(pytz.timezone("EST")).time()
      c = .alpaca.get_alpaca_data(ticker, get_prev_mins_alpaca(15), get_timestamp_alpaca(now.hour, now.minute), 15)
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






#   async def go_long(ticker, price, q=None):
#      with open("trades.pickle", 'rb') as file:
#         trades = pickle.load(file)
#
#      #if tools.get_market_hours_type() == "pre":
#         if trades["rh"]["daytrades"] < 3:
#            await buy_rh(ticker, round(price, 4), q)
#            await send_gmail("Buying On Robin Hood. Ticker: " + ticker + " Price: " + str(price))
#         elif trades["rh_ira"]["daytrades"] < 3:
#            await buy_rh_roth_ira(ticker, round(price, 4), q)
#            await send_gmail("Buying On Robin Hood IRA. Ticker: " + ticker + " Price: " + str(price))
#         elif trades["alpaca"]["daytrades"] < 3:
#            await buy_alpaca(ticker, round(price, 4), q)
#            await send_gmail("Buying Alpaca. Ticker: " + ticker + " Price: " + str(price))
#
#         with open("trades.pickle", 'wb') as file:
#            pickle.dump(trades, file)
#

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

