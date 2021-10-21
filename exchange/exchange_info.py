from typing import BinaryIO
from utils.hyperparameters import SERVER_STATUS, ORDER_ID
from data import orders, conversions, symbol_trade, symbol_book, currently_open_symbols, current_positions_in_symbols 
from utils.data_types import Symbol, Direction, InfoType
from communicate import read_from_exchange


####################
## MAIN FUNCTIONS ##
####################


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

    global currently_open_symbols, symbol_book, symbol_trade, SERVER_STATUS

    print("CLOSING: {}".format(info["symbols"]))
    for symbol in info["symbols"]:
        currently_open_symbols[symbol] = False

    # If the entire market is currently closed and nothing is trading then reset the orderbook and trades log
    if all(currently_open_symbols.keys() == False):
        SERVER_STATUS = 0
        symbol_book, symbol_trade = {symbol: [] for symbol in symbol_book}, {symbol: [] for symbol in symbol_trade}


def handle_error(info):

    print("ERROR: {}".format(info["error"]))


def handle_trade(info):

    global symbol_trade

    symbol_trade[info["symbol"]].append((info["price"], info["size"]))


def handle_ack(info):

    global current_positions_in_symbols

    # Take note of the orderID
    _order_id = info["order_id"]

    # If the orderID has already been seen
    if _order_id in orders:
        direction, symbol, price, size = orders[_order_id] # size or what?
        print(f"Order {_order_id}: Dir - {direction}, Symbol - {symbol}, Price - {price}, Orig - {size} has been placed on the books")
    
    else:

        direction, symbol, size = conversions[_order_id]
        print(f"Order {_order_id}: Dir - {direction}, Symbol - {symbol}, Size - {size} has been converted")

        # Converting between ETF and its components by doing reverse trades and same with ADR and its foreign counterpart

        # Trading cost might be 5 dollars per trade so can take that into account while doing trades
        if symbol == Symbol.VALE:
            current_positions_in_symbols[Symbol.VALE] -= size
            current_positions_in_symbols[Symbol.VALBZ] += size
            current_positions_in_symbols[Symbol.USD] -= 10

        # If it is ETF conversion
        elif symbol == Symbol.XLF:
            # Account for trading costs
            current_positions_in_symbols[Symbol.USD] -= 100

            # If we believe that the ETF is below its fair value, then buy 10 units of that and sell the
            # constituent stocks
            if direction == Direction.BUY:
                current_positions_in_symbols[Symbol.BOND] -= 3
                current_positions_in_symbols[Symbol.GS] -= 2
                current_positions_in_symbols[Symbol.MS] -= 3
                current_positions_in_symbols[Symbol.WFC] -= 2
                current_positions_in_symbols[Symbol.XLF] += 10

            # If we believe that the ETF is overvalued, then sell 10 units of the ETF and buy the
            # constituent stocks
            elif direction == Direction.SELL:
                current_positions_in_symbols[Symbol.BOND] += 3
                current_positions_in_symbols[Symbol.GS] += 2
                current_positions_in_symbols[Symbol.MS] += 3
                current_positions_in_symbols[Symbol.WFC] += 2
                current_positions_in_symbols[Symbol.XLF] -= 10

        print("CURRENT POSITION: {}".format(current_positions_in_symbols))


def handle_fill(info):

    global orders, current_positions_in_symbols

    _order_id = info["order_id"]
    size = info["size"]

    direction, symbol, price, orig, current = orders[_order_id]
    current -= size

    # Partial fills allowed
    orders[_order_id] = (direction, symbol, price, orig, current)

    print(f"Order {_order_id}: Dir - {direction}, Symbol - {symbol}, Price - {price}, Orig - {orig}, Current - {current} has been filled")

    if direction == Direction.SELL:
        current_positions_in_symbols[Symbol.USD] += (price * size)
        current_positions_in_symbols[symbol] -= size
    else:
        current_positions_in_symbols[symbol] += size
    print("CURRENT POSITION: {}".format(current_positions_in_symbols))


def handle_out(info):

    _order_id = info["order_id"]
    print("Order {}: Dir - {}, Symbol - {}, Price - {}, Orig - {}, Current - {} is off the books".format(_order_id, *orders[_order_id]))


def handle_book(info):

    global symbol_book

    symbol_book[info["symbol"]] = { "BUY": info["buy"], "SELL": info["sell"] }


handle = {
    # just print current holdings and record them
    InfoType.HELLO: handle_hello,
    # record the current open symbols
    InfoType.OPEN: handle_open,
    # record the currently closed symbols
    InfoType.CLOSE: handle_close,
    # take note of the trade metadata and store it in symbol trade
    InfoType.ERROR: handle_error,
    # acknoledgement from the server of your trade being placed on the order book
    InfoType.ACK: handle_ack,
    # order has been filled or completed
    InfoType.FILL: handle_fill,
    # order has been removed from the order book
    InfoType.OUT: handle_out,
    # book returned with buy and sell price
    InfoType.BOOK: handle_book
}


def server_info(exchange: BinaryIO) -> None:

    # Set the global variables
    global SERVER_STATUS, ORDER_ID, symbol_trade, symbol_book

    for _ in range(250):

        # Read a input from the exchange
        info = read_from_exchange(exchange)
        # If nothing is returned then break
        if not info:
            break

        handle[info["type"]]()