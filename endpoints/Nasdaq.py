class Nasdaq:
   def get_earnings():
      headers = {"User-Agent": config["settings"]["user_agent"]["value"]}
      today = datetime.now()
      d = today.strftime('%Y-%m-%d')
      response = requests.get("https://api.nasdaq.com/api/calendar/earnings?date=" + d, headers=headers)
      e = response.json()
      for i in e["data"]["rows"]:
         print(d, "\033[92m", i["symbol"], '\033[0m', i["lastYearEPS"], i["epsForecast"])
