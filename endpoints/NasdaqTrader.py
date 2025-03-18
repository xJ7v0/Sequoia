import requests
from lxml import html

class NasdaqTrader:

   def get_halts():
      # URL to send the POST request to
      url = 'https://www.nasdaqtrader.com/RPCHandler.axd'

      # Headers, including the referer from the curl command
      headers = {
          'Referer': 'https://www.nasdaqtrader.com/trader.aspx?id=TradeHalts',
          'Content-Type': 'application/json',  # Assuming the request expects JSON content
      }

      # Data to be sent in the POST request (JSON format)
      data = {
          'id': 2,
          'method': 'BL_TradeHalt.GetTradeHalts',
          'params': [],
          'version': '1.1'
      }

      # Sending the POST request with the data and headers
      response = requests.post(url, json=data, headers=headers)

      # Parse the content with lxml's HTML parser
      tree = html.fromstring(response.text)

      # Extract all <tr> elements
      table_rows = tree.xpath('//tr')

      # Print the content of each <tr>
      for row in table_rows:
         # Find all <td> elements within the <tr>
         cells = row.xpath('.//td')

         if cells:
            # Extract text from each <td> and print
            cell_data = [cell.text.strip() if cell.text else '' for cell in cells]
            return cell_data
