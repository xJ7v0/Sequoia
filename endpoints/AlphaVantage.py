class AlphaVantage:
   def __init__(self, key):
      self.key = key

   def get_news(self, ticker):
      _from = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
      url = "https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=" + ticker + "&time_from=" + _from + "T0000" + "&apikey=" + self.key
      r = requests.get(url)
      data = r.json()
      i = 0
      a = []
      if any("Invalid" in str(value) for value in data.values()):
         print(data["Information"])
      elif data:
         while i < int(data["items"]):
            h = data["feed"][i]["title"]
            date = int(datetime.strptime(data["feed"][i]["time_published"], "%Y%m%dT%H%M%S").timestamp() * 1000)
            a.append((date, h))
            i += 1
         return a
      else:
        print("Empty Data Stream While Recieving From AlphaVantage.")
        return [(0, None)]


