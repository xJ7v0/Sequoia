'''
Scans the small cap market for continuation

Output:
   A list of tickers into a file
'''
import asyncio

class daily_bullish_setup:
   def __init__(self, alpaca):
      self.alpaca = alpaca

   # Single threaded
   async def if_daily_above_10_percent(self):
      symbols = tools.get_symbols()
      candles = {}
      good = []
      now = datetime.now(pytz.timezone("EST"))
      _from = now - timedelta(days=7)
      t = self.get_timestamp()
      for ticker in symbols:
         candles = self.get(ticker, _from.strftime('%Y-%m-%dT%H:%M:%S-05:00'), t, 30, "asc", "1Day", session)
         i = 0
         if c.get("bars") is not None:
            #print(candles["bars"])
            while i < len(c["bars"]):
               if tools.get_percentage(candles["bars"][i]["o"], candles["bars"][i]["c"]) > 10:
                  print(ticker)
                  good += [ticker]
               i += 1

      with open('swing.pickle', 'wb') as f:
         pickle.dump(good, f)

   def main(self):
      asyncio.run(self.alpaca.if_daily_above_10_percent)
