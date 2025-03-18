class GlobeNewswire:

   def get_news(self, ticker):
      headers = {"User-Agent": config["settings"]["user_agent"]["value"]}
      page = requests.get("https://www.globenewswire.com/search/keyword/" + ticker + "?pageSize=25", headers=headers)
      tree = html.fromstring(page.content)
      headlines = tree.xpath('//a[@data-autid="article-url"]/text()')
      dates = tree.xpath('//span[@data-autid="article-published-date"]/text()')
      i = 0
      a = []
      if len(dates) == len(headlines):
         while i < len(dates):
            if "ET" in dates[i]:
               date_obj = datetime.strptime(dates[i].replace(" ET", ""), "%B %d, %Y %H:%M").replace(tzinfo=timezone(timedelta(hours=-5)))
               d = int(date_obj.timestamp() * 1000)
            else:
               print("Fatal Error: Unknown Timezone to parse.", date[i])
               d = 0
            a.append((d, headlines[i]))
            i += 1
         return a
      else:
         print("Fatal Parsing Error in Global News Wire Function, Mismatch in Length of Headlines and Dates.")
         return (0, "None")

