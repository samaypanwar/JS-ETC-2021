from typing import BinaryIO
from utils.hyperparameters import SERVER_STATUS, ORDER_ID
from data import orders, conversions, executed_trades, orderbook, currently_open_symbols, current_positions_in_symbols
from utils.data_types import Ticker, Direction, ResponseType
from exchange.communicate import read_from_exchange


def handle_hello(info):

    global ORDER_ID, current_positions_in_symbols

    print("POSITIONS: {}".format(info["symbols"]))
    symbols = info["symbols"]
    ORDER_ID = 0
    for ticker in symbols:
        current_positions_in_symbols[ticker["symbol"]] = ticker["position"]

def handle_open(info):

    global currently_open_symbols

    print("OPENING: {}".format(info["symbols"]))
    for symbol in info["symbols"]:
        currently_open_symbols[symbol] = True

def handle_close(info):

    global currently_open_symbols, orderbook, executed_trades, SERVER_STATUS

    print("CLOSING: {}".format(info["symbols"]))
    for symbol in info["symbols"]:
        currently_open_symbols[symbol] = False

    # If the entire market is currently closed and nothing is trading then reset the orderbook and trades log
    if all([not symbol for symbol in currently_open_symbols.values()]):
        SERVER_STATUS = 0
        orderbook, executed_trades = {symbol: [] for symbol in orderbook}, {symbol: [] for symbol in executed_trades}

def handle_error(info):

    print("ERROR: {}".format(info["error"]))

def handle_trade(info):

    global executed_trades

    executed_trades[info["symbol"]].append((info["price"], info["size"]))

def handle_ack(info):

    global current_positions_in_symbols, orders, conversions

    # Take note of the orderID
    _order_id = info["order_id"]

    # If the orderID has already been seen
    if _order_id in orders:

        direction = orders[_order_id]['dir']
        symbol = orders[_order_id]['symbol']
        price = orders[_order_id]['price']
        size = orders[_order_id]['size']

        print(f"Order {_order_id}: Dir - {direction}, Symbol - {symbol}, Price - {price}, Orig - {size} has been placed on the books")

    elif _order_id in conversions:
        direction = conversions[_order_id]['dir']
        symbol = conversions[_order_id]['symbol']
        size = conversions[_order_id]['size']

        print(f"Order {_order_id}: Dir - {direction}, Symbol - {symbol}, Size - {size} has been converted")

        # Converting between ETF and its components by doing reverse trades and same with ADR and its foreign counterpart

        # Trading cost might be 5 dollars per trade so can take that into account while doing trades
        if symbol == Ticker.VALE:
            current_positions_in_symbols[Ticker.VALE] -= size
            current_positions_in_symbols[Ticker.VALBZ] += size
            current_positions_in_symbols[Ticker.USD] -= 10

        # If it is ETF conversion
        elif symbol == Ticker.XLF:
            # Account for trading costs
            current_positions_in_symbols[Ticker.USD] -= 100

            # If we believe that the ETF is below its fair value, then buy 10 units of that and sell the
            # constituent stocks
            if direction == Direction.BUY:
                current_positions_in_symbols[Ticker.BOND] -= 3
                current_positions_in_symbols[Ticker.GS] -= 2
                current_positions_in_symbols[Ticker.MS] -= 3
                current_positions_in_symbols[Ticker.WFC] -= 2
                current_positions_in_symbols[Ticker.XLF] += 10

            # If we believe that the ETF is overvalued, then sell 10 units of the ETF and buy the
            # constituent stocks
            elif direction == Direction.SELL:
                current_positions_in_symbols[Ticker.BOND] += 3
                current_positions_in_symbols[Ticker.GS] += 2
                current_positions_in_symbols[Ticker.MS] += 3
                current_positions_in_symbols[Ticker.WFC] += 2
                current_positions_in_symbols[Ticker.XLF] -= 10

    else:
        print(f"OrderID: {_order_id} is not in conversions or orders")

    print("CURRENT POSITION: {}".format(current_positions_in_symbols))

def handle_fill(info):

    global orders, current_positions_in_symbols

    _order_id = info["order_id"]
    size = info["size"]

    # Partial fills allowed
    orig = orders[_order_id]['size']
    orders[_order_id]['size'] -= size
    direction = orders[_order_id]
    symbol = orders[_order_id]['symbol']
    price = orders[_order_id]['price']

    print(f"Order {_order_id}: Dir - {direction}, Symbol - {symbol}, Price - {price}, Orig - {orig}, Remaining - {orders[_order_id]['size']} has been filled")

    if direction == Direction.SELL:
        current_positions_in_symbols[Ticker.USD] += (price * size)
        current_positions_in_symbols[symbol] -= size
    else:
        current_positions_in_symbols[symbol] += size
    print("CURRENT POSITION: {}".format(current_positions_in_symbols))

def handle_out(info):

    global orders

    _order_id = info["order_id"]
    direction = orders[_order_id]['dir']
    symbol = orders[_order_id]['symbol']
    price = orders[_order_id]['price']
    size = orders[_order_id]['size']

    print(f"Order {_order_id}: Dir - {direction}, Symbol - {symbol}, Price - {price}, Size - {size}, is off the books")

def handle_book(info):

    global orderbook

    orderbook[info["symbol"]] = { "BUY": info["buy"], "SELL": info["sell"] }

def handle_reject(info):

    _order_id = info['order_id']
    direction = orders[_order_id]['dir']
    price = orders[_order_id]['price']
    size = orders[_order_id]['size']

    del orders[_order_id]

    if direction == Direction.BUY:
        current_positions_in_symbols[Ticker.USD] += (size * price)

handle = {
    # just print current holdings and record them
    ResponseType.HELLO: handle_hello,
    # record the current open symbols
    ResponseType.OPEN: handle_open,
    # record the currently closed symbols
    ResponseType.CLOSE: handle_close,
    # take note of the trade metadata and store it in symbol trade
    ResponseType.ERROR: handle_error,
    # acknoledgement from the server of your trade being placed on the order book
    ResponseType.ACK: handle_ack,
    # order has been filled or completed
    ResponseType.FILL: handle_fill,
    # order has been removed from the order book
    ResponseType.OUT: handle_out,
    # book returned with buy and sell price
    ResponseType.BOOK: handle_book,

    ResponseType.REJECT: handle_reject,
    ResponseType.TRADE: handle_trade,
    'pass': lambda x: ...
}

def server_response(exchange: BinaryIO) -> None:

    # Set the global variables
    global SERVER_STATUS, ORDER_ID, executed_trades, orderbook

    for _ in range(250):

        # Read a input from the exchange
        info = read_from_exchange(exchange)
        # If nothing is returned then break
        if not info:
            return None

        handle[info["type"]](info)
