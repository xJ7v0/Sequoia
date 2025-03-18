class Polygon:
   def __init__(self, key):
      self.key = key
      self.session = requests.Session()

   def get_prev_mins(self, m=5):
      new_time = datetime.now() - timedelta(minutes=m)
      rounded_time = datetime(
         new_time.year, new_time.month, new_time.day,
         new_time.hour, new_time.minute - new_time.minute % 1, 0, 0
      )
      return math.floor(rounded_time.timestamp() * 1000)

   def get_timestamp(self, h=None, m=None, specific_date=None):
      today = date.today()
      if calendar.day_name[today.weekday()] in ("Saturday", "Sunday") and specific_date is None:
         specific_date =  datetime.strptime(self.get_last_friday(), '%Y-%m-%d')
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

   def if_8_percent_gain_multi(self, ticker, result_queue):
      '''
      Get stocks that have moved 8 percent
      '''

      now = datetime.now(pytz.timezone("EST")).time()
      c = {}
      c = self.get_aggs(ticker, self.get_prev_mins(2), get_timestamp(now.hour, now.minute), 8, "asc", 15, "second")
      i = 0
      symbols = {}
      if c:
         while i < c["resultsCount"]:
            if get_percentage(c["results"][i]["o"], c["results"][i]["c"]) >= float(config["settings"]["upper_percent"]["value"]):
               symbols[ticker] = c["results"][i]
               result_queue.put(symbols)
            i += 1

   def get_aggs(self, ticker, _from, to, limit, sort, multiplier, timespan, result_queue=None):
      '''
       _from		- YYYY-MM-DD or a millisecond timestamp
       to		- YYYY-MM-DD or a millisecond timestamp
       limit		- Max 50000 and Default 5000
       sort		- asc or desc
       multiplier	- size of timespan multiplier
       timespan		- second, minute, hour, day, week, month, quarter, year

       Response Object
       {
         "adjusted": true,
         "next_url": "https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/1578114000000/2020-01-10?cursor=bGltaXQ9MiZzb3J0PWFzYw",
         "queryCount": 2,
         "request_id": "6a7e466379af0a71039d60cc78e72282",
         "results": [
           {
             "c": 75.0875,
             "h": 75.15,
             "l": 73.7975,
             "n": 1,
             "o": 74.06,
             "t": 1577941200000,
             "v": 135647456,
             "vw": 74.6099
           },
           {
             "c": 74.3575,
             "h": 75.145,
             "l": 74.125,
             "n": 1,
             "o": 74.2875,
             "t": 1578027600000,
             "v": 146535512,
             "vw": 74.7026
           }
         ],
         "resultsCount": 2,
         "status": "OK",
         "ticker": "AAPL"
       }
      '''

      if f > t:
         print("Fatal: From time higher than To time!", f, t)
         # EXIT()

      url = "https://api.polygon.io/v2/aggs/ticker/" + ticker + "/range/" + str(m) + "/" + ts + "/" + str(f) + "/" + str(t) + "?adjusted=true&sort=" + s + "&limit=" + str(l) + "&apiKey=" + self.key
      while True:
         try:
            response = self.session.get(url, timeout=2)
            if response.status_code == 200:
               if result_queue:
                  result_queue.put((ticker, response.json()))
               else
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

   def get_news_polygon(ticker):
      f = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%SZ')
      client = RESTClient(api_key=config["polygon"]["api_key"])
      news = []
      for n in client.list_ticker_news(ticker, order="desc", published_utc_gte=f, limit=50):
         news.append(n)

      a = []
      i = 0
      while i < len(news):
         h = news[i].title
         d = int(datetime.strptime(news[i].published_utc, "%Y-%m-%dT%H:%M:%SZ").timestamp() * 1000)
         a.append((d, h))
         i += 1
#      # print date + title
#      for index, item in enumerate(news):
#         # verify this is an agg
#         if isinstance(item, TickerNews):
#            d, h = "{:<25}{:<15}".format(item.published_utc, item.title))
#            if index == 20:
#               break
      return a

