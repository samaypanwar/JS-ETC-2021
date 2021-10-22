from utils.hyperparameters import ORDER_ID
from exchange.communicate import write_to_exchange
from data import orders, current_positions_in_symbols, symbol_book
from utils.data_types import Direction, Symbol
import penny_pinching
import orderbook_filling


def trade_symbol(order_type, symbol, direction, price, size):

    return {
        'type': str(order_type),
        'symbol': symbol,
        'dir': direction,
        'price': price,
        'size': size
    }


def place_trade(list_of_trades, exchange):

    global ORDER_ID, orders, current_positions_in_symbols

    if list_of_trades:
        for trade in list_of_trades:

            trade['order_id'] = ORDER_ID
            write_to_exchange(exchange, trade)
            orders[ORDER_ID] = trade
            ORDER_ID += 1

            if trade['dir'] == str(Direction.BUY):
                current_positions_in_symbols[Symbol.USD] -= trade['size'] * trade['price']

def _bonds_strategy():
    bond_trades = penny_pinching.trade_bonds(symbol_book[Symbol.BOND])
    return bond_trades

def _clear_orderbook():

    symbols = [Symbol.GS, Symbol.WFC, Symbol.MS]
    trades = []

    for symbol in symbols:
        fairvalue = orderbook_filling.calculate_symbol_fair_value(symbol)
        trade = orderbook_filling.clear_symbol_orderbook(symbol_book[symbol], fairvalue, symbol)
        trades.append(trade)

    return trades

def execute_strategy(info, exchange, mode):
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
        trades = _bonds_strategy()
        place_trade(trades, exchange)

    if mode[1] == 1:
        trades = _clear_orderbook()
        place_trade(trades, exchange)

    if mode[2] == 1:
        ...
        # Execute ADR   

    if mode[3] == 1:
        ...
        # Execute ETF