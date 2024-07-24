# No point in fixing since we have stocknewsapi:
# fix businesswire
# parse yesterday news for seeking alpha using date stamp from the server (mostly done)
# check for other tickers in news

# Might not need:
# check volume before buying
# get news within 1 day period

# TODO:
# gap up between open[i] and close[i+1]
# check if ticker is currently moving on the websocket before buying
# check if the order went through
# get stocks from IBKR

# check alpaca to make sure it buys in the premarket
# fix robinhood to buy/sell in the premarket
# fix trades[*][ticker]
# make sure orders go through else cancel them and and do it again
# watch multiple tickers
# sell if green candle is 2% then red candle

# first price to make a new high
# if price > previous red candle open; then buy
# if price < previous green candle ;then sell

# if doji then reversal
#find_channel()

#sell call
# topping tail that is red followed by a red candle
#sell put/buy call
# bottoming tail followed by a green candle
#set break points and invisible stop point
#previous low on previous candle if it goes below, reversal


# Usage: from sequoia import sequoia as ModuleClass

import json

import endpoints, tools, apps

class Sequoia():

   def __init__(self):
      #self.old_symbols_dicts = {}
      #self.trades = {}

      with open("config.json", "r") as jsonfile: self.config = json.load(jsonfile)

      self.robinhood = endpoints.Robinhood(self.config["robinhood"]["user"],
                                 self.config["robinhood"]["password"],
                                 self.config["robinhood"]["device_token"])

      self.alpaca = endpoints.Alpaca(self.config["alpaca"]["api_key"],
                                     self.config["alpaca"]["secret"],
                                     self.robinhood)

      self.polygon = endpoints.Polygon

      self.snapi = endpoints.StockNewsAPI(self.config["stocknewsapi"]["api_key"])


      self.app1 = apps.earnings


   def app1(self):
      self.app1.main()


   def main1():
      #schedule.every().day.at("00:00").do(tools.get_symbols)
      #schedule.every().day.at("05:00").do(tools.get_earnings)
      while True:
         #next
         schedule.run_pending()
         today = date.today()
         if calendar.day_name[today.weekday()] in ("Saturday", "Sunday"):
            t.sleep(60)
         else:
            if time(4, 0) <= datetime.now(pytz.timezone("EST")).time() < time(20, 0):
               d = self.tasks.scan_small_cap()
               if d:
                  if old_d != d:
                     old_d = d
                     print(d)





   # fcl = first candle low
   #async def trade(ticker, price, broker, fcl):

   #   #if get_market_hours_type() == "pre":
   #      # if the price of the stock goes below 7 percent of the low of the first movement candle
   #
   #      #if price <= (c["bars"][-1]["l"] - (c["bars"][-1]["l"] *.07)):
   #      #   await sell(ticker, price)
   #      #   return True
   #      # if a great move happened in 5 minutes sell, [RVSN 1/22/24 148%]
   #      if get_percentage(trades[broker][ticker]["low"], trades[broker][ticker]["high"]) > 40:
   #         if price <= target_sell:
   #            await sell(ticker, price)
   #            return True
   #   elif get_market_hours_type() == "market" or get_market_hours_type() == "post":
   #      if price <= target_sell:
   #         print(ticker, "Target Sell", target_sell)
   #         await sell(ticker, price)
   #         return True
   #
#      return False

