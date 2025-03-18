'''

Buys if a stock goes above 8% and has a press release

'''
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, date, timedelta, time, timezone

import asyncio, pytz

class small_cap_news:
   def __init__(self, symbols, alpaca, snapi):
      self.symbols = symbols
      self.snapi = snapi
      #self.trades =

   def watch_start(self):
      asyncio.run(watch(ticker))

   async def watch(self, ticker):
      p = 0
      to = 0

      stats = {}

      #if not ticker in trades[broker]:
      #trades[broker][ticker] = {}
      #trades[broker][ticker]["high"] = 0
      #trades[broker][ticker]["low"] = sys.maxsize

      now = datetime.now(pytz.timezone("EST")).time()
      c = self.alpaca.get_bars(ticker, self.alpaca.get_prev_mins(15), self.alpaca.get_timestamp(now.hour, now.minute), 15, "asc", "1Min")

      if c.get("bars"):
         if len(c["bars"]) == 1:
            lc = self.alpaca.get_bars(ticker, self.alpaca.get_last_trade_day(), self.alpaca.get_timestamp(now.hour, now.minute), 2000)
            c["bars"] = lc["bars"] + c["bars"]
      else:
         c = get_data(ticker, self.alpaca.get_last_trade_day(), self.alpaca.get_timestamp(now.hour, now.minute), 2000)

      i = 0
      for item in reversed(c["bars"]):
         if i >= 15:
            break
         if item["l"] < trades[broker][ticker]["low"]:
            stats[ticker]["low"] = item["l"]
         if item["h"] > trades[broker][ticker]["high"]:
            stats[ticker]["high"] = item["h"]
         i += 1
         fcl = trades[broker][ticker]["low"]

      ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
      ssl_context.load_verify_locations(certifi.where())
      sub = False
      async for s in connect("wss://stream.data.alpaca.markets/v2/sip", close_timeout=5, ssl=ssl_context):
         try:
            cmsg = await s.recv()
            await s.send(json.dumps({"action": "auth", "key": config["alpaca"]["api_key"], "secret": config["alpaca"]["secret"]}))
            amsg = await s.recv()
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


   async def trade_on_press_release(self):
      n = self.snapi.get_all_tickers_press_releases()
      n["data"].reverse()

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

   def main(self):
      scheduler = AsyncIOScheduler()
      scheduler.add_job(self.trade_on_press_release, trigger=CronTrigger(second=2, minute='*', hour='7-17', day_of_week='mon-fri', timezone=pytz.timezone('US/Eastern')))
      scheduler.start()
      asyncio.get_event_loop().run_forever()
