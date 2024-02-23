from ibapi.wrapper import *
from ibapi.client import *
from ibapi.contract import Contract
from ibapi.wrapper import EWrapper

def create_contract(symbol, sec_type, exchange, currency):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.exchange = exchange
    contract.currency = currency
    return contract

def request_market_data(con, contract):
    class MarketDataHandler(EWrapper, EClient):
        def __init__(self):
            EWrapper.__init__(self)
            EClient.__init__(self, self)

        def error(self, reqId, errorCode, errorString):
            print(f"Error: {errorCode}, {errorString}")

        def tickPrice(self, reqId, tickType, price, attrib):
            print(f"Tick Price. Ticker Id: {reqId}, Type: {tickType}, Price: {price}")

    handler = MarketDataHandler()
    con.connect("127.0.0.1", 4001, clientId=0)
    con.reqMarketDataType(4)
    con.reqMktData(1, contract, "", False, False, [])
    con.disconnect()

def main():
    con = EClient(EWrapper())
    contract = create_contract("AAPL", "STK", "SMART", "USD")
    request_market_data(con, contract)

if __name__ == "__main__":
    main()
