from utils.hyperparameters import ORDER_ID
from exchange.communicate import write_to_exchange
from data import orders, current_positions_in_symbols
from utils.data_types import Direction, Symbol


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