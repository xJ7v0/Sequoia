# get patterns
# weight on calls and puts
#import main




def main():

# check if cash account
# get cash amount
# bet 50%
# range trading
# get options for the spy
# create channels
# reversals










def get_open_option_positions(account_number=None, info=None):
    """Returns all open option positions for the account.
    
    :param acccount_number: the robinhood account number.
    :type acccount_number: Optional[str]
    :param info: Will filter the results to get a specific value.
    :type info: Optional[str]
    :returns: Returns a list of dictionaries of key/value pairs for each option. If info parameter is provided, \
    a list of strings is returned where the strings are the value of the key that matches info.

    """
    url = option_positions_url(account_number=account_number)
    payload = {'nonzero': 'True'}
    data = request_get(url, 'pagination', payload)

    return(filter_data(data, info))

def find_tradable_options(symbol, expirationDate=None, strikePrice=None, optionType=None, info=None):
    """Returns a list of all available options for a stock.

    :param symbol: The ticker of the stock.
    :type symbol: str
    :param expirationDate: Represents the expiration date in the format YYYY-MM-DD.
    :type expirationDate: str
    :param strikePrice: Represents the strike price of the option.
    :type strikePrice: str
    :param optionType: Can be either 'call' or 'put' or left blank to get both.
    :type optionType: Optional[str]
    :param info: Will filter the results to get a specific value.
    :type info: Optional[str]
    :returns: Returns a list of dictionaries of key/value pairs for all calls of the stock. If info parameter is provided, \
    a list of strings is returned where the strings are the value of the key that matches info.

    """
    try:
        symbol = symbol.upper().strip()
    except AttributeError as message:
        print(message, file=get_output())
        return [None]

    url = option_instruments_url()
    if not id_for_chain(symbol):
        print("Symbol {} is not valid for finding options.".format(symbol), file=get_output())
        return [None]

    payload = {'chain_id': id_for_chain(symbol),
               'chain_symbol': symbol,
               'state': 'active'}

    if expirationDate:
        payload['expiration_dates'] = expirationDate
    if strikePrice:
        payload['strike_price'] = strikePrice
    if optionType:
        payload['type'] = optionType

    data = request_get(url, 'pagination', payload)
    return(filter_data(data, info))



# options


def aggregate_url(account_number):
    if account_number:
        return('https://api.robinhood.com/options/aggregate_positions/?account_numbers='+account_number)
    else:
        return('https://api.robinhood.com/options/aggregate_positions/')


def chains_url(symbol):
    return('https://api.robinhood.com/options/chains/{0}/'.format(id_for_chain(symbol)))


def option_historicals_url(id):
    return('https://api.robinhood.com/marketdata/options/historicals/{0}/'.format(id))


def option_instruments_url(id=None):
    if id:
        return('https://api.robinhood.com/options/instruments/{0}/'.format(id))
    else:
        return('https://api.robinhood.com/options/instruments/')


def option_orders_url(orderID=None, account_number=None):
    url = 'https://api.robinhood.com/options/orders/'
    if orderID:
        url += '{0}/'.format(orderID)
    if account_number:
        url += ('?account_numbers='+account_number)

    return url


def option_positions_url(account_number):
    if account_number:
        return('https://api.robinhood.com/options/positions/?account_numbers='+account_number)
    else:
        return('https://api.robinhood.com/options/positions/')


def marketdata_options_url():
    return('https://api.robinhood.com/marketdata/options/')
