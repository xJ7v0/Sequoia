import datetime, pytz, smtplib, calendar

from datetime import datetime, date, timedelta, time, timezone
from email.mime.text import MIMEText

#from pytz import timezone
#from datetime import strptime

class alerts:
   async def send_gmail(body):
      if config["gmail"]["app_password"]:
         msg = MIMEText(body)
         msg['Subject'] = "Stock Alert! " + datetime.now().strftime("%H:%M %m-%d-%Y")
         msg['From'] = config["gmail"]["sender"]
         msg['To'] = ', '.join(config["gmail"]["receiver"])
         with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(config["gmail"]["sender"], config["gmail"]["app_password"])
            smtp_server.sendmail(config["gmail"]["sender"], config["gmail"]["receiver"], msg.as_string())

class tools:
   def get_market_hours_type():
      now = datetime.now(pytz.timezone("EST")).time()
      if datetime.strptime("4:00", "%H:%M").time() <= now < datetime.strptime("9:30", "%H:%M").time():
         return "pre"
      elif datetime.strptime("9:30", "%H:%M").time() <= now < datetime.strptime("15:00", "%H:%M").time():
         return "market"
      elif datetime.strptime("16:00", "%H:%M").time() <= now < datetime.strptime("20:00", "%H:%M").time():
         return "post"
      else:
         return None

   def get_last_friday():
      today = datetime.now(pytz.timezone("EST"))
      days_to_friday = (today.weekday() - 4) % 7
      last_friday = today - timedelta(days=days_to_friday)
      return last_friday.strftime('%Y-%m-%d')

   def get_timestamp(h=None, m=None, specific_date=None):
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




class scanner:
   def __init__(self):
      self.old_symbols_dicts = {}

   def start_scan(self):
      symbols = tools.get_symbols()
      symbols_dicts = {}
      with requests.Session() as session:
         with multiprocessing.Manager() as manager:
            result_queue = manager.Queue()
            with multiprocessing.Pool(processes=multiprocessing.cpu_count() * int(config["settings"]["multiplier"]["value"])) as pool:
               pool.starmap(scan_current_move_poly, [(symbols[i], result_queue, session) for i in range(len(symbols))])

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


