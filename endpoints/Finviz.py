class Finviz:
   def __init__(self, url):
      self.url = url

   def finviz(self):
      symbols_file = "symbols.pickle"
      if os.path.exists(symbols_file) and os.path.getsize(symbols_file) > 0:
         with open(symbols_file, 'rb') as file:
            return pickle.load(file)

      # Market Cap: Under 2B
      # Current Volume: Under 1M
      # Shares Outstanding: Under 10M
      # Price: Under 10
      #url = "https://finviz.com/screener.ashx?v=111&f=cap_smallunder,sh_curvol_u1000,sh_outstanding_u10,sh_price_u10&ft=4&o=-marketcap&r="
      url = self.url
      headers = {"User-Agent": config["settings"]["user_agent"]["value"]}
      page = requests.get(url + "1", headers=headers)
      tree = html.fromstring(page.content)
      lastpage = tree.xpath('//*[@class="screener-pages"]/text()')[-1]
      symbols = []
      i = 0
      while i < int(lastpage):
         newurl = url + str(i*20+1)
         page = requests.get(newurl, headers=headers)
         tree = html.fromstring(page.content)
         symbols += tree.xpath('//*[@class="tab-link"]/text()')[2:22]
         i += 1

      with open(symbols_file, 'wb') as file:
         pickle.dump(sorted(symbols)[:-9], file)

      # Removes junk
      return sorted(symbols)[:-9]
