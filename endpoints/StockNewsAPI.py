class StockNewsAPI:
   def __init__(self, key):
      self.key = key
      self.old_news_all = {}
      self.session = requests.Session()
      self.session.headers = {
         "Accept": "*/*",
         "Connection": "keep-alive"
      }

   def get_all_tickers_press_releases(self):
      while True:
         try:
            response = self.session.get("https://stocknewsapi.com/api/v1/category?section=alltickers&cache=false&items=30&page=1&topic=PressRelease&token=" + self.key, timeout=5)
            if response.status_code == 200:
               return response.json()
            response.raise_for_status()
         except requests.exceptions.Timeout:
            pass
         except requests.exceptions.RequestException as e:
            pass

        # except:
        #    print("Fatal: Couldn't get a valid response from stocknewsapi.com")
        #    return


   def get_press_release(self, ticker):
      response = requests.get("https://stocknewsapi.com/api/v1?tickers=" + ticker + "&items=10&cache=false&page=1&&token=" + self.key)
      n = response.json()
      a = []
      i = 0
      while i < len(n["data"]):
         d = int(datetime.strptime(n["data"][i]["date"], "%a, %d %b %Y %H:%M:%S %z").timestamp() * 1000)
         if "PressRelease" in n["data"][i]["topics"]:
            a.append((d, n["data"][i]["title"]))
         i += 1
      return a
