from strategy.etf import etf_strategy
from utils.hyperparameters import ORDER_ID
from exchange.communicate import write_to_exchange
from data import orders, current_positions_in_symbols, symbol_book, conversions
from utils.data_types import Direction, Symbol, Action
import penny_pinching
import orderbook_filling
from adr import adr_strategy


def trade_symbol(order_type, symbol, direction, price = 0, size = 10):

    if order_type == Action.CONVERT:
        return {
        'type': str(order_type),
        'symbol': symbol,
        'dir': direction,
        'size': size
    }

    elif order_type == Action.ADD:
        return {
            'type': str(order_type),
            'symbol': symbol,
            'dir': direction,
            'price': price,
            'size': size
        }


def place_trade(list_of_trades, exchange):

    global ORDER_ID, orders, current_positions_in_symbols, conversions

    if list_of_trades:
        for trade in list_of_trades:

            trade['order_id'] = ORDER_ID
            write_to_exchange(exchange, trade)
            if trade['type'] == Action.CONVERT:
                conversions[ORDER_ID] = trade
                ORDER_ID += 1

            elif trade['type'] == Action.ADD:
                orders[ORDER_ID] = trade
                ORDER_ID += 1

            if trade['dir'] == str(Direction.BUY):
                current_positions_in_symbols[Symbol.USD] -= trade['size'] * trade['price']

def bonds_strategy():
    bond_trades = penny_pinching.trade_bonds(symbol_book[Symbol.BOND])
    return bond_trades

def clear_orderbook():

    symbols = [Symbol.GS, Symbol.WFC, Symbol.MS]
    trades = []

    for symbol in symbols:
        new_trades = orderbook_filling.clear_symbol_orderbook(symbol)
        trades.extend(new_trades)

    return trades

def execute_strategy(exchange, mode):
    """Execute Trades

    Parameters
    ----------
    mode : List of bits
        index 0: Bonds
        index 1: stocks orderbook fairvalue
        index 2: adr
        index 3: etf conversion
    """

    global ORDER_ID, symbol_book

    if mode[0] == 1:
        trades = bonds_strategy()
        place_trade(trades, exchange)

    if mode[1] == 1:
        trades = clear_orderbook()
        place_trade(trades, exchange)

    if mode[2] == 1:
        trades = adr_strategy()
        place_trade(trades, exchange)

    if mode[3] == 1:
        trades = etf_strategy()
        place_trade(trades, exchange)