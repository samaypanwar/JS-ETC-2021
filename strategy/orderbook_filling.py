from utils.data_types import *
from utils.hyperparameters import *
from strategy import trade_symbol

def clear_symbol_orderbook(symbol_orderbook, fair_value, symbol_name) -> List[Trade]:
    """See if any of the securities are below their fairvalue and then see if any orders in the orderbook
    have an oppurtunity of arbitrage

    Returns
    -------
    List[Dict]
        Returns a list of trades to make
    """

    buy_order = {
                'size': 0,
                'price': 0
                }

    sell_order = {
                'size': 0,
                'price': LARGE_NUMBER
                }

    trades = []

    for price, size in symbol_orderbook['BUY']:

        if price > fair_value:
            sell_order['size'] += size
            sell_order['price'] = min(sell_order['price'], price)

    for price, size in symbol_orderbook['SELL']:

        if price < fair_value:
            buy_order['size'] += size
            buy_order['price'] = max(buy_order['price'], price)

    if sell_order['size'] > 0:
        trade = trade_symbol(Action.ADD, symbol_name, Direction.SELL, sell_order['price'], sell_order['size'])
        trades.append(trade)

    if buy_order['size'] > 0:
        trade = trade_symbol(Action.ADD, symbol_name, Direction.BUY, sell_order['price'], sell_order['size'])
        trades.append(trade)

    return trades