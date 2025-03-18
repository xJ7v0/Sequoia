#mrket maker movement: 50 cents instantly
'''
Turbo SPY options scalper
'''

import tkinter as tk
import os


class TurboOptionScalper:
   def __init__(self, robinhood):
      self.robinhood = robinhood
      self.setting1_var = ""
      self.contracts_per_trade = 1
      self.trades_per_day = 4

      if os.path.exists("TurboOptionScalper.json"):
         with open("TurboOptionScalper.json", "r") as f: self.trades = json.load(f)
      else:
         self.trades = {"calls": 0, "puts": 0}

   def btn_buy_call(self):
      if self.setting1_var.get() == True:
         if self.trades["puts"] > 0:
            self.robinhood.option_order("SPY", "put", "sell", self.trades["puts"])
         elif self.trades["puts"] < 0:
            print("apps: turboscalper: puts: fatal under 0")

      account = self.robinhood.load_account_profile("traditional")
      bp = float(account["buying_power"]) / self.trades_per_day

      result = self.robinhood.option_order("SPY", "call", "buy", self.contracts_per_trade)
      if result["cancel_url"] is None:
         trades["calls"] += 1
         print("call order went through")

#{"account_number":"","cancel_url":"https:\/\/api.robinhood.com\/options\/orders\/66b6c0e4-67fe-4ff1-9427-642aa3c23619\/cancel\/","canceled_quantity":"0.00000","created_at":"2024-08-10T01:22:44.427572Z","direction":"debit","id":"66b6c0e4-67fe-4ff1-9427-642aa3c23619","legs":[{"executions":[],"id":"66b6c0e4-2055-42c8-a5bf-fe89c7312029","option":"https:\/\/api.robinhood.com\/options\/instruments\/d594291b-0a70-4d6a-afd1-f0c62cd92f6c\/","position_effect":"open","ratio_quantity":1,"side":"buy","expiration_date":"2024-08-12","strike_price":"625.0000","option_type":"call","long_strategy_code":"d594291b-0a70-4d6a-afd1-f0c62cd92f6c_L1","short_strategy_code":"d594291b-0a70-4d6a-afd1-f0c62cd92f6c_S1"}],"pending_quantity":"1.00000","premium":"1.00000000","processed_premium":"0","net_amount":"0","net_amount_direction":"debit","price":"0.01000000","processed_quantity":"0.00000","quantity":"1.00000","ref_id":"af8ed93b-2493-430a-ab70-a01d5e26a377","regulatory_fees":"0","state":"unconfirmed","time_in_force":"gfd","trigger":"immediate","type":"limit","updated_at":"2024-08-10T01:22:44.427601Z","chain_id":"c277b118-58d9-4060-8dc5-a3b5898955cb","chain_symbol":"SPY","response_category":null,"opening_strategy":"long_call","closing_strategy":null,"stop_price":null,"form_source":"option_chain","client_bid_at_submission":"0E-8","client_ask_at_submission":"0.01000000","client_time_at_submission":null,"average_net_premium_paid":"0.00000000","estimated_total_net_amount":"1.03","estimated_total_net_amount_direction":"debit","is_replaceable":false,"strategy":"long_call"}
#{"account_number":"","cancel_url":"https:\/\/api.robinhood.com\/options\/orders\/66b6c0e4-67fe-4ff1-9427-642aa3c23619\/cancel\/","canceled_quantity":"0.00000","created_at":"2024-08-10T01:22:44.427572Z","direction":"debit","id":"66b6c0e4-67fe-4ff1-9427-642aa3c23619","legs":[{"executions":[],"id":"66b6c0e4-2055-42c8-a5bf-fe89c7312029","option":"https:\/\/api.robinhood.com\/options\/instruments\/d594291b-0a70-4d6a-afd1-f0c62cd92f6c\/","position_effect":"open","ratio_quantity":1,"side":"buy","expiration_date":"2024-08-12","strike_price":"625.0000","option_type":"call","long_strategy_code":"d594291b-0a70-4d6a-afd1-f0c62cd92f6c_L1","short_strategy_code":"d594291b-0a70-4d6a-afd1-f0c62cd92f6c_S1"}],"pending_quantity":"1.00000","premium":"1.00000000","processed_premium":"0","net_amount":"0","net_amount_direction":"debit","price":"0.01000000","processed_quantity":"0.00000","quantity":"1.00000","ref_id":"af8ed93b-2493-430a-ab70-a01d5e26a377","regulatory_fees":"0","state":"queued","time_in_force":"gfd","trigger":"immediate","type":"limit","updated_at":"2024-08-10T01:22:44.742467Z","chain_id":"c277b118-58d9-4060-8dc5-a3b5898955cb","chain_symbol":"SPY","response_category":null,"opening_strategy":"long_call","closing_strategy":null,"stop_price":null,"form_source":"option_chain","client_bid_at_submission":"0E-8","client_ask_at_submission":"0.01000000","client_time_at_submission":null,"average_net_premium_paid":"0.00000000","estimated_total_net_amount":"1.03","estimated_total_net_amount_direction":"debit","is_replaceable":false,"strategy":"long_call"}
   def btn_buy_put(self):
      if self.setting1_var.get() == True:
         if self.trades["calls"] > 0:
            self.robinhood.option_order("SPY", "call", "sell", self.trades["calls"])
         elif self.trades["calls"] < 0:
            print("apps: turboscalper: calls: fatal under 0")

      self.robinhood.option_order("SPY", "put", "buy", self.contracts_per_trade)


   def btn_close(self):
      if self.trades["puts"] > 0:
         self.robinhood.option_order("SPY", "put", "sell", self.trades["puts"])

      if self.trades["calls"] > 0:
         self.robinhood.option_order("SPY", "call", "sell", self.trades["calls"])

   def main(self):
      root = tk.Tk()
      root.title("Turbo SPY scalper")

      self.setting1_var = tk.BooleanVar()
      right_frame = tk.Frame(root)
      right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

      setting1 = tk.Checkbutton(right_frame, text="Sell opposite type on button press", variable=self.setting1_var)
      setting1.pack(pady=10, side="top")
      setting1.toggle()


      btn_buy_call = tk.Button(root, text="Buy Call", command=self.btn_buy_call, width=20, height=3, font=("Helvetica", 16))
      btn_buy_call.pack(pady=10)

      btn_buy_put = tk.Button(root, text="Buy Put", command=self.btn_buy_put, width=20, height=3, font=("Helvetica", 16))
      btn_buy_put.pack(pady=10)

      btn_close = tk.Button(root, text="Close All", command=self.btn_close, width=20, height=3, font=("Helvetica", 16))
      btn_close.pack(pady=10)

      root.mainloop()
