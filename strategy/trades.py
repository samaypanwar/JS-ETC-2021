from utils.hyperparameters import ORDER_ID
from exchange.communicate import write_to_exchange
from data import orders, current_positions_in_symbols, conversions
from utils.data_types import Direction, Ticker, Action

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
                current_positions_in_symbols[Ticker.USD] -= trade['size'] * trade['price']
