from utils.data_types import *
from utils.hyperparameters import *
from strategy.trades import trade_symbol
from data import orderbook, currently_open_symbols

def clear_symbol_orderbook(symbol):
    """See if any of the securities are below their fairvalue and then see if any orders in the orderbook
    have an oppurtunity of arbitrage
    """

    if currently_open_symbols[symbol] == False : return []

    buy_order = {
                'size': 0,
                'price': 0
                }

    sell_order = {
                'size': 0,
                'price': LARGE_NUMBER
                }

    trades = []

    symbol_orderbook = orderbook[symbol]
    fair_value = calculate_fair_value(symbol, directional=False)

    for price, size in symbol_orderbook['BUY']:
        if price > fair_value:
            sell_order['size'] += size
            sell_order['price'] = min(sell_order['price'], price)

    for price, size in symbol_orderbook['SELL']:
        if price < fair_value:
            buy_order['size'] += size
            buy_order['price'] = max(buy_order['price'], price)

    if sell_order['size'] > 0:
        trade = trade_symbol(Action.ADD, symbol, Direction.SELL, sell_order['price'], sell_order['size'])
        trades.append(trade)

    if buy_order['size'] > 0:
        trade = trade_symbol(Action.ADD, symbol, Direction.BUY, sell_order['price'], sell_order['size'])
        trades.append(trade)

    return trades

def calculate_fair_value(symbol, trim = 0.1, directional=False, direction=None):
    """Calculates the fairvalue of the symbol based on the most recent orderbook snapshot we have.

    Parameters
    ----------
    symbol : str
        one of the three stocks: MS, GS, WFC

    Returns
    -------
    float
        trimmed mean of the prices quoted in the orderbook
    """

    global orderbook
    most_recent_orderbook = orderbook[symbol]

    if directional == False:
        prices = [x[0] for x in [most_recent_orderbook["BUY"] + most_recent_orderbook["SELL"]]]

    else:
        prices = [x[0] for x in most_recent_orderbook[direction]]

    prices = sorted(prices)
    right_cut = int(len(prices) * trim)
    left_cut = int(len(prices) * (1-trim))

    mean = sum(prices[right_cut: left_cut]) / len(prices[right_cut: left_cut])

    return mean