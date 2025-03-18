class SeekingAlpha:

   def get_news_seekingalpha(self, ticker):
      #date Fri, 19 Jan 2024 00:14:59 GMT
      headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8", "Cookie": "session_id=9340b026-098a-46b7-a5d9-975884014f64; _sasource=; machine_cookie=8473266229581; LAST_VISITED_PAGE=%7B%22pathname%22%3A%22https%3A%2F%2Fseekingalpha.com%2Fsymbol%2FAVBP%22%2C%22pageKey%22%3A%22ee9c0b70-dcd3-4c2d-94bb-9f33860941a4%22%7D; _pcid=%7B%22browserId%22%3A%22lrjvgsd0aqqhwh99%22%7D; _pcus=eyJ1c2VyU2VnbWVudHMiOm51bGx9; __pat=-18000000; _pctx=%7Bu%7DN4IgrgzgpgThIC4B2YA2qA05owMoBcBDfSREQpAeyRCwgEt8oBJAE0RXQF8g; xbc=%7Bkpex%7Dhd3_VtZ0GbqMa1hUbFMRzw-w4GKfXlC35UKXSyc2ZW6Cb3GaCquVA7Jefj64EOw9wO_tM1QlPzYBgjjVqJek0TbEQf1mPw4k0lmSIgJwrwjuyi7NdoOOay7OvWAuGQxklBJRYR-GSuJj-mTe9CG95k3qANJDuckTcj92-6oCnOulLVbUspxcqPCKhuv7GAaDMMe6xkZjUf7-u5iIlpFkOpeVZQJcR8GDB40v7PW8rSwaP9Bj-baRD7-JLESFRCphgCBgQBvqSsK4WxX2LTkHfbrw5JXdSUI2ZflIngIqmIOBjxbBiuV2dL4EYtDwX7GlB5Ij5SgBzemqQXsT_QikcA; pxcts=ead6f22a-b65d-11ee-a571-1db1f80fda7b; _pxvid=ead6dd7f-b65d-11ee-a571-98e9e854011b; session_id=5109c3c4-1daf-4a4f-a910-eca689bc611d; _sasource=; __pvi=eyJpZCI6InYtMjAyNC0wMS0yNC0wNC01MS00Ni03NzMtQjFiVXZ2N1VJNlZyTjZsRS1jZDFhNTY4ODI5MTJjOWJmNzNhZWMzYmQ5MmQxOTFiOCIsImRvbWFpbiI6Ii5zZWVraW5nYWxwaGEuY29tIiwidGltZSI6MTcwNjA5NzE5NTk5MX0%3D; _pxhd=6d70a2b6f78b1cfd2110e137d19cfa4d06ebdd1d6688314ec21c9d85b8a4d293:d02fc780-65bc-11e9-b971-bb43e5539738; __tbc=%7Bkpex%7DNXqkO49Wa1TE33qISPPjnyvMuzKk30WAYF-ucpD-5E8wA75AfFmA_eSFgY7p3f_X", "User-Agent": config["settings"]["user_agent"]["value"], "Host": "seekingalpha.com"}
      page = requests.get("https://seekingalpha.com/symbol/" + ticker, headers=headers)
      server_time = page.headers.get("date")
      tree = html.fromstring(page.content)
      headlines = tree.xpath('//a[@data-test-id="post-list-item-title"]/text()')
      dates = tree.xpath('//span[@data-test-id="post-list-date"]/text()')
      i = 0
      a = []
      current_year = datetime.now().year
      if len(dates) == len(headlines):
         while i < len(dates):
            if "Yesterday" in dates[i] or "Today" in dates[i]:
               target_date = datetime.strptime(server_time, "%a, %d %b %Y %H:%M:%S %Z").date()
               current_date = datetime.now().date()
               # Calculate yesterday's date
               #yesterday_date = current_date - timedelta(days=1)
               yesterday_date = target_date - timedelta(days=1)
               print(yesterday_date)
               if target_date == current_date:
                  today_date_est = datetime.now(pytz.timezone('US/Eastern')).date()
                  full_datetime_string = f"{today_date_est} {dates[i](',')[1].strip()}"
                  full_datetime = est_timezone.localize(datetime.strptime(full_datetime_string, "%Y-%m-%d %I:%M %p"))
                  d = int(full_datetime.timestamp() * 1000)
                  print("seeking alpha today", d)
               #elif target_date == yesterday_date:
               elif current_date == yesterday_date:
                  print("Broken")
            else:
               try:
                  if '.' in dates[i]:
                     d = int(datetime.strptime(dates[i], "%a, %b. %d, %Y").timestamp() * 1000)
                  else:
                     d = int(datetime.strptime(dates[i], "%a, %b %d, %Y").timestamp() * 1000)
               except ValueError:
                  if '.' in dates[i]:
                     d = int(datetime.strptime(dates[i] + ", " + str(datetime.now().year), "%a, %b. %d, %Y").timestamp() * 1000)
                  else:
                     d = int(datetime.strptime(dates[i] + ", " + str(datetime.now().year), "%a, %b %d, %Y").timestamp() * 1000)

            a.append((d, headlines[i]))
            i += 1
         return a
      else:
         print("Fatal Parsing Error in Seeking Alpha News Function, Mismatch in Length of Headlines and Dates.")
         return (0, "None")

