class StockAnalysis:
   def stockanalysis(self):
      #https://stockanalysis.com/api/screener/s/d/volume.json
      #https://stockanalysis.com/api/screener/s/i
      symbols_file = "symbols.pickle"
      if os.path.exists(symbols_file) and os.path.getsize(symbols_file) > 0:
         with open(symbols_file, 'rb') as file:
            return pickle.load(file)

      d = {}
      dt = []
      headers = {"User-Agent": config["settings"]["user_agent"]["value"]}
      prices = requests.get("https://stockanalysis.com/api/screener/s/d/price.json", headers=headers).json()
      float_ = requests.get("https://stockanalysis.com/api/screener/s/d/float.json", headers=headers).json()
      i = 0
      if prices["status"] == 200:
         while i < len(prices["data"]["data"]):
            if prices["data"]["data"][i][1] <= float(config["settings"]["max_price"]["value"]):
               t = prices["data"]["data"][i][0]
               d[t] = [prices["data"]["data"][i][1]]
            i += 1

         if float_["status"] == 200:
            for ticker in d:
               found = 0
               i = 0
               while i < len(float_["data"]["data"]):
                  if ticker == float_["data"]["data"][i][0]:
                     if float_["data"]["data"][i][1] <= int(config["settings"]["max_float"]["value"]):
                        d[ticker] += [float_["data"]["data"][i][1]]
                     else:
                        dt += [ticker]
                     found = 1
                  i += 1
               if not found:
                  d[ticker] += [None]

            # delete tickers from the dict that dont meat the requirements
            for i in dt:
               del d[i]

      symbols = []
      for i in d:
         symbols.append(i)

      with open(symbols_file, 'wb') as file:
         pickle.dump(symbols, file)

      return symbols
