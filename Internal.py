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
   def milliseconds_to_time_date(m):
      return datetime(1970, 1, 1) + timedelta(seconds=(m / 1000.0))

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


   def get_percentage(open, close):
      return ((close-open)/open)*100

   # false:
   #print(fibonacci_retracement(swing_high, swing_low, 23.6))
   #print(fibonacci_retracement(swing_high, swing_low, 38.2))
   #print(fibonacci_retracement(swing_high, swing_low, 50))
   #print(fibonacci_retracement(swing_high, swing_low, 61.8))
   #print(fibonacci_retracement(swing_high, swing_low, 78.6))
   def fibonacci_retracement(swing_high, swing_low, retracement_percentage):
      return swing_low + (retracement_percentage / 100) * (swing_high - swing_low)


