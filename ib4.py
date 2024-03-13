import socket
import math
import sys
from _decimal import Decimal

NO_VALID_ID = -1
MAX_MSG_LEN = 0xFFFFFF  # 16Mb - 1byte
UNSET_INTEGER = 2**31 - 1
UNSET_DOUBLE = float(sys.float_info.max)
UNSET_LONG = 2**63 - 1
UNSET_DECIMAL = Decimal(2**127 - 1)
DOUBLE_INFINITY = math.inf
INFINITY_STR = "Infinity"

# field types
INT = 1
STR = 2
FLT = 3


# incoming msg id's
class IN:
    TICK_PRICE = 1
    TICK_SIZE = 2
    ORDER_STATUS = 3
    ERR_MSG = 4
    OPEN_ORDER = 5
    ACCT_VALUE = 6
    PORTFOLIO_VALUE = 7
    ACCT_UPDATE_TIME = 8
    NEXT_VALID_ID = 9
    CONTRACT_DATA = 10
    EXECUTION_DATA = 11
    MARKET_DEPTH = 12
    MARKET_DEPTH_L2 = 13
    NEWS_BULLETINS = 14
    MANAGED_ACCTS = 15
    RECEIVE_FA = 16
    HISTORICAL_DATA = 17
    BOND_CONTRACT_DATA = 18
    SCANNER_PARAMETERS = 19
    SCANNER_DATA = 20
    TICK_OPTION_COMPUTATION = 21
    TICK_GENERIC = 45
    TICK_STRING = 46
    TICK_EFP = 47
    CURRENT_TIME = 49
    REAL_TIME_BARS = 50
    FUNDAMENTAL_DATA = 51
    CONTRACT_DATA_END = 52
    OPEN_ORDER_END = 53
    ACCT_DOWNLOAD_END = 54
    EXECUTION_DATA_END = 55
    DELTA_NEUTRAL_VALIDATION = 56
    TICK_SNAPSHOT_END = 57
    MARKET_DATA_TYPE = 58
    COMMISSION_REPORT = 59
    POSITION_DATA = 61
    POSITION_END = 62
    ACCOUNT_SUMMARY = 63
    ACCOUNT_SUMMARY_END = 64
    VERIFY_MESSAGE_API = 65
    VERIFY_COMPLETED = 66
    DISPLAY_GROUP_LIST = 67
    DISPLAY_GROUP_UPDATED = 68
    VERIFY_AND_AUTH_MESSAGE_API = 69
    VERIFY_AND_AUTH_COMPLETED = 70
    POSITION_MULTI = 71
    POSITION_MULTI_END = 72
    ACCOUNT_UPDATE_MULTI = 73
    ACCOUNT_UPDATE_MULTI_END = 74
    SECURITY_DEFINITION_OPTION_PARAMETER = 75
    SECURITY_DEFINITION_OPTION_PARAMETER_END = 76
    SOFT_DOLLAR_TIERS = 77
    FAMILY_CODES = 78
    SYMBOL_SAMPLES = 79
    MKT_DEPTH_EXCHANGES = 80
    TICK_REQ_PARAMS = 81
    SMART_COMPONENTS = 82
    NEWS_ARTICLE = 83
    TICK_NEWS = 84
    NEWS_PROVIDERS = 85
    HISTORICAL_NEWS = 86
    HISTORICAL_NEWS_END = 87
    HEAD_TIMESTAMP = 88
    HISTOGRAM_DATA = 89
    HISTORICAL_DATA_UPDATE = 90
    REROUTE_MKT_DATA_REQ = 91
    REROUTE_MKT_DEPTH_REQ = 92
    MARKET_RULE = 93
    PNL = 94
    PNL_SINGLE = 95
    HISTORICAL_TICKS = 96
    HISTORICAL_TICKS_BID_ASK = 97
    HISTORICAL_TICKS_LAST = 98
    TICK_BY_TICK = 99
    ORDER_BOUND = 100
    COMPLETED_ORDER = 101
    COMPLETED_ORDERS_END = 102
    REPLACE_FA_END = 103
    WSH_META_DATA = 104
    WSH_EVENT_DATA = 105
    HISTORICAL_SCHEDULE = 106
    USER_INFO = 107


# outgoing msg id's
class OUT:
    REQ_MKT_DATA = 1
    CANCEL_MKT_DATA = 2
    PLACE_ORDER = 3
    CANCEL_ORDER = 4
    REQ_OPEN_ORDERS = 5
    REQ_ACCT_DATA = 6
    REQ_EXECUTIONS = 7
    REQ_IDS = 8
    REQ_CONTRACT_DATA = 9
    REQ_MKT_DEPTH = 10
    CANCEL_MKT_DEPTH = 11
    REQ_NEWS_BULLETINS = 12
    CANCEL_NEWS_BULLETINS = 13
    SET_SERVER_LOGLEVEL = 14
    REQ_AUTO_OPEN_ORDERS = 15
    REQ_ALL_OPEN_ORDERS = 16
    REQ_MANAGED_ACCTS = 17
    REQ_FA = 18
    REPLACE_FA = 19
    REQ_HISTORICAL_DATA = 20
    EXERCISE_OPTIONS = 21
    REQ_SCANNER_SUBSCRIPTION = 22
    CANCEL_SCANNER_SUBSCRIPTION = 23
    REQ_SCANNER_PARAMETERS = 24
    CANCEL_HISTORICAL_DATA = 25
    REQ_CURRENT_TIME = 49
    REQ_REAL_TIME_BARS = 50
    CANCEL_REAL_TIME_BARS = 51
    REQ_FUNDAMENTAL_DATA = 52
    CANCEL_FUNDAMENTAL_DATA = 53
    REQ_CALC_IMPLIED_VOLAT = 54
    REQ_CALC_OPTION_PRICE = 55
    CANCEL_CALC_IMPLIED_VOLAT = 56
    CANCEL_CALC_OPTION_PRICE = 57
    REQ_GLOBAL_CANCEL = 58
    REQ_MARKET_DATA_TYPE = 59
    REQ_POSITIONS = 61
    REQ_ACCOUNT_SUMMARY = 62
    CANCEL_ACCOUNT_SUMMARY = 63
    CANCEL_POSITIONS = 64
    VERIFY_REQUEST = 65
    VERIFY_MESSAGE = 66
    QUERY_DISPLAY_GROUPS = 67
    SUBSCRIBE_TO_GROUP_EVENTS = 68
    UPDATE_DISPLAY_GROUP = 69
    UNSUBSCRIBE_FROM_GROUP_EVENTS = 70
    START_API = 71
    VERIFY_AND_AUTH_REQUEST = 72
    VERIFY_AND_AUTH_MESSAGE = 73
    REQ_POSITIONS_MULTI = 74
    CANCEL_POSITIONS_MULTI = 75
    REQ_ACCOUNT_UPDATES_MULTI = 76
    CANCEL_ACCOUNT_UPDATES_MULTI = 77
    REQ_SEC_DEF_OPT_PARAMS = 78
    REQ_SOFT_DOLLAR_TIERS = 79
    REQ_FAMILY_CODES = 80
    REQ_MATCHING_SYMBOLS = 81
    REQ_MKT_DEPTH_EXCHANGES = 82
    REQ_SMART_COMPONENTS = 83
    REQ_NEWS_ARTICLE = 84
    REQ_NEWS_PROVIDERS = 85
    REQ_HISTORICAL_NEWS = 86
    REQ_HEAD_TIMESTAMP = 87
    REQ_HISTOGRAM_DATA = 88
    CANCEL_HISTOGRAM_DATA = 89
    CANCEL_HEAD_TIMESTAMP = 90
    REQ_MARKET_RULE = 91
    REQ_PNL = 92
    CANCEL_PNL = 93
    REQ_PNL_SINGLE = 94
    CANCEL_PNL_SINGLE = 95
    REQ_HISTORICAL_TICKS = 96
    REQ_TICK_BY_TICK_DATA = 97
    CANCEL_TICK_BY_TICK_DATA = 98
    REQ_COMPLETED_ORDERS = 99
    REQ_WSH_META_DATA = 100
    CANCEL_WSH_META_DATA = 101
    REQ_WSH_EVENT_DATA = 102
    CANCEL_WSH_EVENT_DATA = 103
    REQ_USER_INFO = 104


class Order(Object):
    def __init__(self):
        self.softDollarTier = SoftDollarTier("", "", "")
        # order identifier
        self.orderId = 0
        self.clientId = 0
        self.permId = 0

        # main order fields
        self.action = ""
        self.totalQuantity = UNSET_DECIMAL
        self.orderType = ""
        self.lmtPrice = UNSET_DOUBLE
        self.auxPrice = UNSET_DOUBLE

        # extended order fields
        self.tif = ""  # "Time in Force" - DAY, GTC, etc.
        self.activeStartTime = ""  # for GTC orders
        self.activeStopTime = ""  # for GTC orders
        self.ocaGroup = ""  # one cancels all group name
        self.ocaType = (
            0  # 1 = CANCEL_WITH_BLOCK, 2 = REDUCE_WITH_BLOCK, 3 = REDUCE_NON_BLOCK
        )
        self.orderRef = ""
        self.transmit = True  # if false, order will be created but not transmited
        self.parentId = 0  # Parent order id, to associate Auto STP or TRAIL orders with the original order.
        self.blockOrder = False
        self.sweepToFill = False
        self.displaySize = 0
        self.triggerMethod = 0  # 0=Default, 1=Double_Bid_Ask, 2=Last, 3=Double_Last, 4=Bid_Ask, 7=Last_or_Bid_Ask, 8=Mid-point
        self.outsideRth = False
        self.hidden = False
        self.goodAfterTime = ""  # Format: 20060505 08:00:00 {time zone}
        self.goodTillDate = ""  # Format: 20060505 08:00:00 {time zone}
        self.rule80A = ""  # Individual = 'I', Agency = 'A', AgentOtherMember = 'W', IndividualPTIA = 'J', AgencyPTIA = 'U', AgentOtherMemberPTIA = 'M', IndividualPT = 'K', AgencyPT = 'Y', AgentOtherMemberPT = 'N'
        self.allOrNone = False
        self.minQty = UNSET_INTEGER  # type: int
        self.percentOffset = UNSET_DOUBLE  # type: float  # REL orders only
        self.overridePercentageConstraints = False
        self.trailStopPrice = UNSET_DOUBLE  # type: float
        self.trailingPercent = UNSET_DOUBLE  # type: float  # TRAILLIMIT orders only

        # financial advisors only
        self.faGroup = ""
        self.faMethod = ""
        self.faPercentage = ""

        # institutional (ie non-cleared) only
        self.designatedLocation = ""  # used only when shortSaleSlot=2
        self.openClose = ""  # O=Open, C=Close
        self.origin = CUSTOMER  # 0=Customer, 1=Firm
        self.shortSaleSlot = (
            0
        )  # type: int  # 1 if you hold the shares, 2 if they will be delivered from elsewhere.  Only for Action=SSHORT
        self.exemptCode = -1

        # SMART routing only
        self.discretionaryAmt = 0
        self.optOutSmartRouting = False

        # BOX exchange orders only
        self.auctionStrategy = (
            AUCTION_UNSET
        )  # type: int  # AUCTION_MATCH, AUCTION_IMPROVEMENT, AUCTION_TRANSPARENT
        self.startingPrice = UNSET_DOUBLE  # type: float
        self.stockRefPrice = UNSET_DOUBLE  # type: float
        self.delta = UNSET_DOUBLE  # type: float

        # pegged to stock and VOL orders only
        self.stockRangeLower = UNSET_DOUBLE  # type: float
        self.stockRangeUpper = UNSET_DOUBLE  # type: float

        self.randomizePrice = False
        self.randomizeSize = False

        # VOLATILITY ORDERS ONLY
        self.volatility = UNSET_DOUBLE  # type: float
        self.volatilityType = UNSET_INTEGER  # type: int  # 1=daily, 2=annual
        self.deltaNeutralOrderType = ""
        self.deltaNeutralAuxPrice = UNSET_DOUBLE  # type: float
        self.deltaNeutralConId = 0
        self.deltaNeutralSettlingFirm = ""
        self.deltaNeutralClearingAccount = ""
        self.deltaNeutralClearingIntent = ""
        self.deltaNeutralOpenClose = ""
        self.deltaNeutralShortSale = False
        self.deltaNeutralShortSaleSlot = 0
        self.deltaNeutralDesignatedLocation = ""
        self.continuousUpdate = False
        self.referencePriceType = UNSET_INTEGER  # type: int  # 1=Average, 2 = BidOrAsk

        # COMBO ORDERS ONLY
        self.basisPoints = UNSET_DOUBLE  # type: float  # EFP orders only
        self.basisPointsType = UNSET_INTEGER  # type: int  # EFP orders only

        # SCALE ORDERS ONLY
        self.scaleInitLevelSize = UNSET_INTEGER  # type: int
        self.scaleSubsLevelSize = UNSET_INTEGER  # type: int
        self.scalePriceIncrement = UNSET_DOUBLE  # type: float
        self.scalePriceAdjustValue = UNSET_DOUBLE  # type: float
        self.scalePriceAdjustInterval = UNSET_INTEGER  # type: int
        self.scaleProfitOffset = UNSET_DOUBLE  # type: float
        self.scaleAutoReset = False
        self.scaleInitPosition = UNSET_INTEGER  # type: int
        self.scaleInitFillQty = UNSET_INTEGER  # type: int
        self.scaleRandomPercent = False
        self.scaleTable = ""

        # HEDGE ORDERS
        self.hedgeType = ""  # 'D' - delta, 'B' - beta, 'F' - FX, 'P' - pair
        self.hedgeParam = ""  # 'beta=X' value for beta hedge, 'ratio=Y' for pair hedge

        # Clearing info
        self.account = ""  # IB account
        self.settlingFirm = ""
        self.clearingAccount = ""  # True beneficiary of the order
        self.clearingIntent = ""  # "" (Default), "IB", "Away", "PTA" (PostTrade)

        # ALGO ORDERS ONLY
        self.algoStrategy = ""

        self.algoParams = None  # TagValueList
        self.smartComboRoutingParams = None  # TagValueList

        self.algoId = ""

        # What-if
        self.whatIf = False

        # Not Held
        self.notHeld = False
        self.solicited = False

        # models
        self.modelCode = ""

        # order combo legs

        self.orderComboLegs = None  # OrderComboLegListSPtr

        self.orderMiscOptions = None  # TagValueList

        # VER PEG2BENCH fields:
        self.referenceContractId = 0
        self.peggedChangeAmount = 0.0
        self.isPeggedChangeAmountDecrease = False
        self.referenceChangeAmount = 0.0
        self.referenceExchangeId = ""
        self.adjustedOrderType = ""

        self.triggerPrice = UNSET_DOUBLE
        self.adjustedStopPrice = UNSET_DOUBLE
        self.adjustedStopLimitPrice = UNSET_DOUBLE
        self.adjustedTrailingAmount = UNSET_DOUBLE
        self.adjustableTrailingUnit = 0
        self.lmtPriceOffset = UNSET_DOUBLE

        self.conditions = []  # std::vector<std::shared_ptr<OrderCondition>>
        self.conditionsCancelOrder = False
        self.conditionsIgnoreRth = False

        # ext operator
        self.extOperator = ""

        # native cash quantity
        self.cashQty = UNSET_DOUBLE

        self.mifid2DecisionMaker = ""
        self.mifid2DecisionAlgo = ""
        self.mifid2ExecutionTrader = ""
        self.mifid2ExecutionAlgo = ""

        self.dontUseAutoPriceForHedge = False

        self.isOmsContainer = False

        self.discretionaryUpToLimitPrice = False

        self.autoCancelDate = ""
        self.filledQuantity = UNSET_DECIMAL
        self.refFuturesConId = 0
        self.autoCancelParent = False
        self.shareholder = ""
        self.imbalanceOnly = False
        self.routeMarketableToBbo = False
        self.parentPermId = 0

        self.usePriceMgmtAlgo = None
        self.duration = UNSET_INTEGER
        self.postToAts = UNSET_INTEGER
        self.advancedErrorOverride = ""
        self.manualOrderTime = ""
        self.minTradeQty = UNSET_INTEGER
        self.minCompeteSize = UNSET_INTEGER
        self.competeAgainstBestOffset = UNSET_DOUBLE
        self.midOffsetAtWhole = UNSET_DOUBLE
        self.midOffsetAtHalf = UNSET_DOUBLE

    def __str__(self):
        s = "%s,%s,%s:" % (
            intMaxString(self.orderId),
            intMaxString(self.clientId),
            intMaxString(self.permId),
        )

        s += " %s %s %s@%s" % (
            self.orderType,
            self.action,
            decimalMaxString(self.totalQuantity),
            floatMaxString(self.lmtPrice),
        )

        s += f" {self.tif}"

        if self.orderComboLegs:
            s += " CMB("
            for leg in self.orderComboLegs:
                s += str(leg) + ","
            s += ")"

        if self.conditions:
            s += " COND("
            for cond in self.conditions:
                s += str(cond) + ","
            s += ")"

        return s


class Contract(Object):
    def __init__(self):
        self.conId = 0
        self.symbol = ""
        self.secType = ""
        self.lastTradeDateOrContractMonth = ""
        self.strike = 0.0  # float !!
        self.right = ""
        self.multiplier = ""
        self.exchange = ""
        self.primaryExchange = ""  # pick an actual (ie non-aggregate) exchange that the contract trades on.
        # DO NOT SET TO SMART.
        self.currency = ""
        self.localSymbol = ""
        self.tradingClass = ""
        self.includeExpired = False
        self.secIdType = ""  # CUSIP;SEDOL;ISIN;RIC
        self.secId = ""
        self.description = ""
        self.issuerId = ""

        # combos
        self.comboLegsDescrip = (
            ""
        )  # type: str #received in open order 14 and up for all combos
        self.comboLegs = []  # type: list[ComboLeg]
        self.deltaNeutralContract = None

    def __str__(self):
        s = ",".join(
            (
                str(self.conId),
                str(self.symbol),
                str(self.secType),
                str(self.lastTradeDateOrContractMonth),
                floatMaxString(self.strike),
                str(self.right),
                str(self.multiplier),
                str(self.exchange),
                str(self.primaryExchange),
                str(self.currency),
                str(self.localSymbol),
                str(self.tradingClass),
                str(self.includeExpired),
                str(self.secIdType),
                str(self.secId),
                str(self.description),
                str(self.issuerId),
            )
        )
        s += "combo:" + self.comboLegsDescrip

        if self.comboLegs:
            for leg in self.comboLegs:
                s += ";" + str(leg)

        if self.deltaNeutralContract:
            s += ";" + str(self.deltaNeutralContract)

        return s


class IBKR:
   def placeorder():
        try:

            # send place order msg
            flds = []
            flds += [make_field(OUT.PLACE_ORDER)]

            if self.serverVersion() < MIN_SERVER_VER_ORDER_CONTAINER:
                flds += [make_field(VERSION)]

            flds += [make_field(orderId)]

            # send contract fields
            if self.serverVersion() >= MIN_SERVER_VER_PLACE_ORDER_CONID:
                flds.append(make_field(contract.conId))
            flds += [
                make_field(contract.symbol),
                make_field(contract.secType),
                make_field(contract.lastTradeDateOrContractMonth),
                make_field(contract.strike),
                make_field(contract.right),
                make_field(contract.multiplier),  # srv v15 and above
                make_field(contract.exchange),
                make_field(contract.primaryExchange),  # srv v14 and above
                make_field(contract.currency),
                make_field(contract.localSymbol),
            ]  # srv v2 and above
            if self.serverVersion() >= MIN_SERVER_VER_TRADING_CLASS:
                flds.append(make_field(contract.tradingClass))

            if self.serverVersion() >= MIN_SERVER_VER_SEC_ID_TYPE:
                flds += [make_field(contract.secIdType), make_field(contract.secId)]

            # send main order fields
            flds.append(make_field(order.action))

            if self.serverVersion() >= MIN_SERVER_VER_FRACTIONAL_POSITIONS:
                flds.append(make_field(order.totalQuantity))
            else:
                flds.append(make_field(int(order.totalQuantity)))

            flds.append(make_field(order.orderType))
            if self.serverVersion() < MIN_SERVER_VER_ORDER_COMBO_LEGS_PRICE:
                flds.append(
                    make_field(order.lmtPrice if order.lmtPrice != UNSET_DOUBLE else 0)
                )
            else:
                flds.append(make_field_handle_empty(order.lmtPrice))
            if self.serverVersion() < MIN_SERVER_VER_TRAILING_PERCENT:
                flds.append(
                    make_field(order.auxPrice if order.auxPrice != UNSET_DOUBLE else 0)
                )
            else:
                flds.append(make_field_handle_empty(order.auxPrice))

                # send extended order fields
                flds += [
                    make_field(order.tif),
                    make_field(order.ocaGroup),
                    make_field(order.account),
                    make_field(order.openClose),
                    make_field(order.origin),
                    make_field(order.orderRef),
                    make_field(order.transmit),
                    make_field(order.parentId),  # srv v4 and above
                    make_field(order.blockOrder),  # srv v5 and above
                    make_field(order.sweepToFill),  # srv v5 and above
                    make_field(order.displaySize),  # srv v5 and above
                    make_field(order.triggerMethod),  # srv v5 and above
                    make_field(order.outsideRth),  # srv v5 and above
                    make_field(order.hidden),
                ]  # srv v7 and above

            ######################################################################
            # Send the shares allocation.
            #
            # This specifies the number of order shares allocated to each Financial
            # Advisor managed account. The format of the allocation string is as
            # follows:
            #                      <account_code1>/<number_shares1>,<account_code2>/<number_shares2>,...N
            # E.g.
            #              To allocate 20 shares of a 100 share order to account 'U101' and the
            #      residual 80 to account 'U203' enter the following share allocation string:
            #          U101/20,U203/80
            #####################################################################
            # send deprecated sharesAllocation field
            flds += [
                make_field(""),  # srv v9 and above
                make_field(order.discretionaryAmt),  # srv v10 and above
                make_field(order.goodAfterTime),  # srv v11 and above
                make_field(order.goodTillDate),  # srv v12 and above
                make_field(order.faGroup),  # srv v13 and above
                make_field(order.faMethod),  # srv v13 and above
                make_field(order.faPercentage),
            ]  # srv v13 and above
            #if self.serverVersion() < MIN_SERVER_VER_FA_PROFILE_DESUPPORT:
            #    flds.append(make_field(""))  # send deprecated faProfile field

            if self.serverVersion() >= MIN_SERVER_VER_MODELS_SUPPORT:
                flds.append(make_field(order.modelCode))

            # institutional short saleslot data (srv v18 and above)
            flds += [
                make_field(
                    order.shortSaleSlot
                ),  # 0 for retail, 1 or 2 for institutions
                make_field(order.designatedLocation),
            ]  # populate only when shortSaleSlot = 2.
            if self.serverVersion() >= MIN_SERVER_VER_SSHORTX_OLD:
                flds.append(make_field(order.exemptCode))

            # srv v19 and above fields
            flds.append(make_field(order.ocaType))
            # if( self.serverVersion() < 38) {
            # will never happen
            #      send( /* order.rthOnly */ false)
            # }
            flds += [
                make_field(order.rule80A),
                make_field(order.settlingFirm),
                make_field(order.allOrNone),
                make_field_handle_empty(order.minQty),
                make_field_handle_empty(order.percentOffset),
                make_field(False),
                make_field(False),
                make_field_handle_empty(UNSET_DOUBLE),
                make_field(
                    order.auctionStrategy
                ),  # AUCTION_MATCH, AUCTION_IMPROVEMENT, AUCTION_TRANSPARENT
                make_field_handle_empty(order.startingPrice),
                make_field_handle_empty(order.stockRefPrice),
                make_field_handle_empty(order.delta),
                make_field_handle_empty(order.stockRangeLower),
                make_field_handle_empty(order.stockRangeUpper),
                make_field(order.overridePercentageConstraints),  # srv v22 and above
                # Volatility orders (srv v26 and above)
                make_field_handle_empty(order.volatility),
                make_field_handle_empty(order.volatilityType),
                make_field(order.deltaNeutralOrderType),  # srv v28 and above
                make_field_handle_empty(order.deltaNeutralAuxPrice),
            ]  # srv v28 and above

            if (
                self.serverVersion() >= MIN_SERVER_VER_DELTA_NEUTRAL_CONID
                and order.deltaNeutralOrderType
            ):
                flds += [
                    make_field(order.deltaNeutralConId),
                    make_field(order.deltaNeutralSettlingFirm),
                    make_field(order.deltaNeutralClearingAccount),
                    make_field(order.deltaNeutralClearingIntent),
                ]

            if (
                self.serverVersion() >= MIN_SERVER_VER_DELTA_NEUTRAL_OPEN_CLOSE
                and order.deltaNeutralOrderType
            ):
                flds += [
                    make_field(order.deltaNeutralOpenClose),
                    make_field(order.deltaNeutralShortSale),
                    make_field(order.deltaNeutralShortSaleSlot),
                    make_field(order.deltaNeutralDesignatedLocation),
                ]

            flds += [
                make_field(order.continuousUpdate),
                make_field_handle_empty(order.referencePriceType),
                make_field_handle_empty(order.trailStopPrice),
            ]  # srv v30 and above

            if self.serverVersion() >= MIN_SERVER_VER_TRAILING_PERCENT:
                flds.append(make_field_handle_empty(order.trailingPercent))

            # SCALE orders
            if self.serverVersion() >= MIN_SERVER_VER_SCALE_ORDERS2:
                flds += [
                    make_field_handle_empty(order.scaleInitLevelSize),
                    make_field_handle_empty(order.scaleSubsLevelSize),
                ]
            else:
                # srv v35 and above)
                flds += [
                    make_field(""),  # for not supported scaleNumComponents
                    make_field_handle_empty(order.scaleInitLevelSize),
                ]  # for scaleComponentSize

            flds.append(make_field_handle_empty(order.scalePriceIncrement))

            if (
                self.serverVersion() >= MIN_SERVER_VER_SCALE_ORDERS3
                and order.scalePriceIncrement != UNSET_DOUBLE
                and order.scalePriceIncrement > 0.0
            ):
                flds += [
                    make_field_handle_empty(order.scalePriceAdjustValue),
                    make_field_handle_empty(order.scalePriceAdjustInterval),
                    make_field_handle_empty(order.scaleProfitOffset),
                    make_field(order.scaleAutoReset),
                    make_field_handle_empty(order.scaleInitPosition),
                    make_field_handle_empty(order.scaleInitFillQty),
                    make_field(order.scaleRandomPercent),
                ]

            if self.serverVersion() >= MIN_SERVER_VER_SCALE_TABLE:
                flds += [
                    make_field(order.scaleTable),
                    make_field(order.activeStartTime),
                    make_field(order.activeStopTime),
                ]

            # HEDGE orders
            if self.serverVersion() >= MIN_SERVER_VER_HEDGE_ORDERS:
                flds.append(make_field(order.hedgeType))
                if order.hedgeType:
                    flds.append(make_field(order.hedgeParam))

            if self.serverVersion() >= MIN_SERVER_VER_OPT_OUT_SMART_ROUTING:
                flds.append(make_field(order.optOutSmartRouting))

            if self.serverVersion() >= MIN_SERVER_VER_PTA_ORDERS:
                flds += [
                    make_field(order.clearingAccount),
                    make_field(order.clearingIntent),
                ]

            if self.serverVersion() >= MIN_SERVER_VER_NOT_HELD:
                flds.append(make_field(order.notHeld))

            if self.serverVersion() >= MIN_SERVER_VER_DELTA_NEUTRAL:
                if contract.deltaNeutralContract:
                    flds += [
                        make_field(True),
                        make_field(contract.deltaNeutralContract.conId),
                        make_field(contract.deltaNeutralContract.delta),
                        make_field(contract.deltaNeutralContract.price),
                    ]
                else:
                    flds.append(make_field(False))

            if self.serverVersion() >= MIN_SERVER_VER_ALGO_ORDERS:
                flds.append(make_field(order.algoStrategy))
                if order.algoStrategy:
                    algoParamsCount = len(order.algoParams) if order.algoParams else 0
                    flds.append(make_field(algoParamsCount))
                    if algoParamsCount > 0:
                        for algoParam in order.algoParams:
                            flds += [
                                make_field(algoParam.tag),
                                make_field(algoParam.value),
                            ]

            if self.serverVersion() >= MIN_SERVER_VER_ALGO_ID:
                flds.append(make_field(order.algoId))

            flds.append(make_field(order.whatIf))  # srv v36 and above

            # send miscOptions parameter
            if self.serverVersion() >= MIN_SERVER_VER_LINKING:
                miscOptionsStr = ""
                if order.orderMiscOptions:
                    for tagValue in order.orderMiscOptions:
                        miscOptionsStr += str(tagValue)
                flds.append(make_field(miscOptionsStr))

            if self.serverVersion() >= MIN_SERVER_VER_ORDER_SOLICITED:
                flds.append(make_field(order.solicited))

            if self.serverVersion() >= MIN_SERVER_VER_RANDOMIZE_SIZE_AND_PRICE:
                flds += [
                    make_field(order.randomizeSize),
                    make_field(order.randomizePrice),
                ]

            if self.serverVersion() >= MIN_SERVER_VER_PEGGED_TO_BENCHMARK:
                if isPegBenchOrder(order.orderType):
                    flds += [
                        make_field(order.referenceContractId),
                        make_field(order.isPeggedChangeAmountDecrease),
                        make_field(order.peggedChangeAmount),
                        make_field(order.referenceChangeAmount),
                        make_field(order.referenceExchangeId),
                    ]

                flds.append(make_field(len(order.conditions)))

                if len(order.conditions) > 0:
                    for cond in order.conditions:
                        flds.append(make_field(cond.type()))
                        flds += cond.make_fields()

                    flds += [
                        make_field(order.conditionsIgnoreRth),
                        make_field(order.conditionsCancelOrder),
                    ]

                flds += [
                    make_field(order.adjustedOrderType),
                    make_field(order.triggerPrice),
                    make_field(order.lmtPriceOffset),
                    make_field(order.adjustedStopPrice),
                    make_field(order.adjustedStopLimitPrice),
                    make_field(order.adjustedTrailingAmount),
                    make_field(order.adjustableTrailingUnit),
                ]

            if self.serverVersion() >= MIN_SERVER_VER_EXT_OPERATOR:
                flds.append(make_field(order.extOperator))

            if self.serverVersion() >= MIN_SERVER_VER_SOFT_DOLLAR_TIER:
                flds += [
                    make_field(order.softDollarTier.name),
                    make_field(order.softDollarTier.val),
                ]

            if self.serverVersion() >= MIN_SERVER_VER_CASH_QTY:
                flds.append(make_field(order.cashQty))

            if self.serverVersion() >= MIN_SERVER_VER_DECISION_MAKER:
                flds.append(make_field(order.mifid2DecisionMaker))
                flds.append(make_field(order.mifid2DecisionAlgo))

            if self.serverVersion() >= MIN_SERVER_VER_MIFID_EXECUTION:
                flds.append(make_field(order.mifid2ExecutionTrader))
                flds.append(make_field(order.mifid2ExecutionAlgo))

            if self.serverVersion() >= MIN_SERVER_VER_AUTO_PRICE_FOR_HEDGE:
                flds.append(make_field(order.dontUseAutoPriceForHedge))

            if self.serverVersion() >= MIN_SERVER_VER_ORDER_CONTAINER:
                flds.append(make_field(order.isOmsContainer))

            if self.serverVersion() >= MIN_SERVER_VER_D_PEG_ORDERS:
                flds.append(make_field(order.discretionaryUpToLimitPrice))

            if self.serverVersion() >= MIN_SERVER_VER_PRICE_MGMT_ALGO:
                flds.append(
                    make_field_handle_empty(
                        UNSET_INTEGER
                        if order.usePriceMgmtAlgo is None
                        else 1
                        if order.usePriceMgmtAlgo
                        else 0
                    )
                )

            if self.serverVersion() >= MIN_SERVER_VER_DURATION:
                flds.append(make_field(order.duration))

            if self.serverVersion() >= MIN_SERVER_VER_POST_TO_ATS:
                flds.append(make_field(order.postToAts))

            if self.serverVersion() >= MIN_SERVER_VER_AUTO_CANCEL_PARENT:
                flds.append(make_field(order.autoCancelParent))

            if self.serverVersion() >= MIN_SERVER_VER_ADVANCED_ORDER_REJECT:
                flds.append(make_field(order.advancedErrorOverride))

            if self.serverVersion() >= MIN_SERVER_VER_MANUAL_ORDER_TIME:
                flds.append(make_field(order.manualOrderTime))

            if self.serverVersion() >= MIN_SERVER_VER_PEGBEST_PEGMID_OFFSETS:
                sendMidOffsets = False
                if contract.exchange == "IBKRATS":
                    flds.append(make_field_handle_empty(order.minTradeQty))
                if isPegBestOrder(order.orderType):
                    flds.append(make_field_handle_empty(order.minCompeteSize))
                    flds.append(make_field_handle_empty(order.competeAgainstBestOffset))
                    if (
                        order.competeAgainstBestOffset
                        == COMPETE_AGAINST_BEST_OFFSET_UP_TO_MID
                    ):
                        sendMidOffsets = True
                elif isPegMidOrder(order.orderType):
                    sendMidOffsets = True
                if sendMidOffsets:
                    flds.append(make_field_handle_empty(order.midOffsetAtWhole))
                    flds.append(make_field_handle_empty(order.midOffsetAtHalf))

            msg = "".join(flds)

        except ClientException as ex:
            self.wrapper.error(orderId, ex.code, ex.msg + ex.text)
            return

        self.sendMsg(msg)

mycontract = Contract()
mycontract.symbol = "AAPL"
mycontract.secType = "STK"
mycontract.exchange = "SMART"
mycontract.currency = "USD"



from ibapi.client import *
from ibapi.wrapper import *
class TestApp(EClient, EWrapper):
  def __init__(self):
    EClient.__init__(self, self)
  def nextValidId(self, orderId: OrderId):
    mycontract = Contract()
    mycontract.symbol = "AAPL"
    mycontract.secType = "STK"    
    mycontract.exchange = "SMART"
    mycontract.currency = "USD"
    self.reqContractDetails(orderId, mycontract)
  def contractDetails(self, reqId: int, contractDetails: ContractDetails):
    print(contractDetails.contract)
    myorder = Order()
    myorder.orderId = reqId
    myorder.action = "SELL"
    myorder.tif = "GTC"
    myorder.orderType = "LMT"
    myorder.lmtPrice = 144.80
    myorder.totalQuantity = 10
    self.placeOrder(myorder.orderId, contractDetails.contract, myorder)
  def openOrder(self, orderId: OrderId, contract: Contract, order: Order, orderState: OrderState):
    print(f"openOrder. orderId: {orderId}, contract: {contract}, order: {order}")
  def orderStatus(self, orderId: OrderId, status: str, filled: Decimal, remaining: Decimal, avgFillPrice: float, permId: int, parentId: int, lastFillPrice: float, clientId: int, whyHeld: str, mktCapPrice: float):
    print(f"orderId: {orderId}, status: {status}, filled: {filled}, remaining: {remaining}, avgFillPrice: {avgFillPrice}, permId: {permId}, parentId: {parentId}, lastFillPrice: {lastFillPrice}, clientId: {clientId}, whyHeld: {whyHeld}, mktCapPrice: {mktCapPrice}")
  def execDetails(self, reqId: int, contract: Contract, execution: Execution):
    print(f"reqId: {reqId}, contract: {contract}, execution: {execution}")
app = TestApp()
app.connect("127.0.0.1", 7497, 100)
app.run()
