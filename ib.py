from ibapi.client import *
from ibapi.wrapper import *
from ibapi.contract import Contract
from ibapi.ticktype import TickTypeEnum

class TestApp(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)

#    def nextValidId(self, orderId: int):
#        mycontract = Contract()
#        mycontract.symbol = "AAPL"
#        mycontract.secType = "STK"
#        mycontract.exchange = "SMART"
#        mycontract.currency = "USD"
#        self.reqMarketDataType(4)
#        self.reqMktData(orderId, mycontract, "", 0, 0, [])

    def tickPrice(self, reqId, tickType, price, attrib):
        print(f"tickPrice. reqId: {reqId}, tickType: {TickTypeEnum.toStr(tickType)}, price: {price}, attribs: {attrib}")

    def tickSize(self, reqId, tickType, size):
        print(f"tickSize. reqId: {reqId}, tickType: {TickTypeEnum.toStr(tickType)}, size: {size}")




app = TestApp()
app.connect("127.0.0.1", 4001, clientId=1)
print("serverVersion:%s connectionTime:%s" % (app.serverVersion(), app.twsConnectionTime()))
print(app.isConnected())

contract = Contract()
contract.symbol = "AAPL"
contract.secType = "STK"
contract.exchange = "SMART"
contract.currency = "USD"
contract.primaryExchange = "NASDAQ"

app.reqMarketDataType(1)
app.reqMktData(1, contract, "", False, False, [])


app.run()
#app.stop()
print("yes")

#from ibapi.contract import Contract
#contract = Contract()
#contract.symbol = "ES"
#contract.secType = "FUT"
#contract.currency = "USD"
#contract.exchange = "GLOBEX"
#contract.localSymbol="ESH9"
#
#app.reqMktData(1, contract, "", False, False, [])
