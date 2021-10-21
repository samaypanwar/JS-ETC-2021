from typing import BinaryIO
from exchange.communicate import write_to_exchange
from utils.hyperparameters import *
from data import *
from utils.data_types import *
from communicate import read_from_exchange
from strategy import penny_pinching, orderbook_filling

####################
## MAIN FUNCTIONS ##
####################

def server_info(exchange: BinaryIO) -> None:

    # Set the global variables
    global SERVER_STATUS
    global ORDER_ID
    global symbol_trade
    global symbol_book

    iterations = 0

    while iterations < 250:

        # Read a input from the exchange
        info = read_from_exchange(exchange)
        iterations += 1

        # If nothing is returned then break
        if not info:
            break

        # What is the type of information returned to us from the server
        info_type = info["type"]

        # If it is hello then just print current holdings and record them
        if info_type == str(InfoType.HELLO):
            print("POSITIONS: {}".format(info["symbols"]))
            symbols = info["symbols"]
            ORDER_ID = 0
            for ticker in symbols:
                current_positions_in_symbols[ticker["symbol"]] = ticker["position"]

        # If the type returned is the open status of the market the record the current open symbols
        elif info_type == str(InfoType.OPEN):
            print("OPENING: {}".format(info["symbols"]))
            for symbol in info["symbols"]:
                currently_open_symbols[symbol] = True

        # If the type returned is the close status, record the currently closed symbols
        elif info_type == str(InfoType.CLOSE):
            print("CLOSING: {}".format(info["symbols"]))

            for symbol in info["symbols"]:
                currently_open_symbols[symbol] = False

            # If the entire market is currently closed and nothing is trading then reset the orderbook and trades log
            if all(currently_open_symbols.keys() == False):
                SERVER_STATUS = 0

                symbol_trade = {
                    "BOND": [],
                    "GS": [],
                    "MS": [],
                    "USD": [],
                    "VALBZ": [],
                    "VALE": [],
                    "WFC": [],
                    "XLF": []
                }

                symbol_book = {
                    "BOND": {},
                    "GS": {},
                    "MS": {},
                    "USD": {},
                    "VALBZ": {},
                    "VALE": {},
                    "WFC": {},
                    "XLF": {}
                }

        elif info_type == str(InfoType.ERROR):
            print("ERROR: {}".format(info["error"]))

        # If the order type returned is 'trade', take note of the trade metadata and store it in symbol trade
        elif info_type == str(InfoType.TRADE):
            symbol_trade[info["symbol"]].append((info["price"], info["size"]))

        # If the return type is an acknoledgement from the server of your trade being placed on the order book
        elif info_type == str(InfoType.ACK):

            # Take note of the orderID
            _order_id = info["order_id"]

            # If the orderID has already been seen
            if _order_id in orders:
                order = orders[_order_id]
                print("Order {}: Dir - {}, Symbol - {}, Price - {}, Orig - {} has been placed on the books"
                        .format(_order_id, order[0], order[1], order[2], order[3], order[4]))
            else:
                conversion = conversions[_order_id]
                print("Order {}: Dir - {}, Symbol - {}, Size - {} has been converted"
                        .format(_order_id, conversion[0], conversion[1], conversion[2]))

                # Converting between ETF and its components by doing reverse trades and same with ADR and its foreign counterpart

                # Trading cost might be 5 dollars per trade so can take that into account while doing trades
                if conversion[1] == str(Symbol.VALE):
                    current_positions_in_symbols[str(Symbol.VALE)] -= conversion[2]
                    current_positions_in_symbols[str(Symbol.VALBZ)] += conversion[2]
                    current_positions_in_symbols[str(Symbol.USD)] -= 10

                # If it is ETF conversion
                elif conversion[1] == str(Symbol.XLF):
                    # Account for trading costs
                    current_positions_in_symbols[str(Symbol.USD)] -= 100

                    # If we believe that the ETF is below its fair value, then buy 10 units of that and sell the
                    # constituent stocks
                    if conversion[0] == str(Direction.BUY):
                        current_positions_in_symbols[str(Symbol.BOND)] -= 3
                        current_positions_in_symbols[str(Symbol.GS)] -= 2
                        current_positions_in_symbols[str(Symbol.MS)] -= 3
                        current_positions_in_symbols[str(Symbol.WFC)] -= 2
                        current_positions_in_symbols[str(Symbol.XLF)] += 10

                    # If we believe that the ETF is overvalued, then sell 10 units of the ETF and buy the
                    # constituent stocks
                    elif conversion[0] == str(Direction.SELL):
                        current_positions_in_symbols[str(Symbol.BOND)] += 3
                        current_positions_in_symbols[str(Symbol.GS)] += 2
                        current_positions_in_symbols[str(Symbol.MS)] += 3
                        current_positions_in_symbols[str(Symbol.WFC)] += 2
                        current_positions_in_symbols[str(Symbol.XLF)] -= 10

                print("CURRENT POSITION: {}".format(current_positions_in_symbols))

        # If the info type is if a order has been filled or completed
        elif info_type == str(InfoType.FILL):
            _order_id = info["order_id"]
            order = orders[_order_id]
            price = order[2]
            size = info["size"]

            # Partial fills allowed
            orders[_order_id] = (order[0], order[1], order[2], order[3], order[4] - size)
            order = orders[_order_id]

            print("Order {}: Dir - {}, Symbol - {}, Price - {}, Orig - {}, Current - {} has been filled"
                    .format(_order_id, order[0], order[1], order[2], order[3], order[4]))

            if order[0] == str(Direction.SELL):
                current_positions_in_symbols[str(Symbol.USD)] += (price * size)
                current_positions_in_symbols[str(order[1])] -= size
            else:
                current_positions_in_symbols[str(order[1])] += size
            print("CURRENT POSITION: {}".format(current_positions_in_symbols))

        elif info_type == str(InfoType.OUT):
            _order_id = info["order_id"]
            order = orders[_order_id]
            print("Order {}: Dir - {}, Symbol - {}, Price - {}, Orig - {}, Current - {} is off the books"
                    .format(_order_id, order[0], order[1], order[2], order[3], order[4]))

        elif info_type == str(InfoType.BOOK):
            symbol = info["symbol"]
            symbol_book[symbol] = {"BUY": info["buy"], "SELL": info["sell"]}

            if symbol == Symbol.BOND:
                bond_trades = penny_pinching.trade_bonds(symbol_book[Symbol.BOND])

                if bond_trades:
                    for trade in bond_trades:

                        trade['order_id'] = ORDER_ID
                        write_to_exchange(exchange, trade)
                        orders[ORDER_ID] = trade
                        ORDER_ID += 1

                        if trade['dir'] == str(Direction.BUY):
                            current_positions_in_symbols[Symbol.USD] -= trade['size'] * trade['price']

            if symbol != Symbol.BOND and symbol not in ['ADR', 'XLF']:


                fairvalue = calculate_symbol_fair_value(symbol)
                trades = orderbook_filling.clear_symbol_orderbook(symbol_book[symbol], fairvalue, symbol)

                if trades:

                    for trade in trades:
                        trade['order_id'] = ORDER_ID
                        write_to_exchange(exchange, trade)
                        orders[ORDER_ID] = trade
                        ORDER_ID += 1

                        if trade['dir'] == str(Direction.BUY):
                            current_positions_in_symbols[Symbol.USD] -= trade['size'] * trade['price']

            # Make another for clearing XLF
            # One for ADR