class momo_scanner:
   def __init__(self, polygon, snapi):
      self.polygon = polygon
      self.snapi = snapi

   #def watch(self, ticker):
   # polygon.watch

   def parse_news(ticker):
      a = sorted(self.snapi.get_press_release(ticker), reverse=True)
      #sorted_array = sorted(a, key=lambda x: x[0], reverse=True)
      if a:
         if get_prev_mins(3) <= a[0][0]:
            print("Breaking News:", tools.milliseconds_to_time_date(a[0][0]), a[0][1])
            asyncio.run(watch_and_buy(ticker))

      i = 0
      while i < len(a):
         for keyword in config["settings"]["news_good"]["value"]:
            if any(word.lower() == keyword.lower() for word in a[i][1].split()):
               print("Previous News:", "Keyword:", keyword, tools.milliseconds_to_time_date(a[i][0]), a[i][1])
         i += 1

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


   def main():
      while True:
         #next
         schedule.run_pending()
         today = date.today()
         if calendar.day_name[today.weekday()] in ("Saturday", "Sunday"):
            t.sleep(60)
         else:
            if time(4, 0) <= datetime.now(pytz.timezone("EST")).time() < time(20, 0):
               d = self.scan_small_cap()
               if d:
                  if old_d != d:
                     old_d = d
                     print(d)

