from utils.hyperparameters import *
from data import *
from init_exchange import *
from utils.data_types import *

####################
## MAIN FUNCTIONS ##
####################

def server_info(exchange: BinaryIO) -> None:
    global SERVER_STATUS
    global ORDER_ID
    global symbol_trade
    global symbol_book

    iterations = 0

    while iterations < 250:
        info = read_from_exchange(exchange)
        iterations += 1
        if not info:
            break
        info_type = info["type"]

        if info_type == str(InfoType.HELLO):
            print("POSITIONS: {}".format(info["symbols"]))
            symbols = info["symbols"]
            ORDER_ID = 0
            for symbol in symbols:
                symbol_positions[symbol["symbol"]] = symbol["position"]
        elif info_type == str(InfoType.OPEN):
            print("OPENING: {}".format(info["symbols"]))
            for symbol in info["symbols"]:
                symbol_open[symbol] = True
        elif info_type == str(InfoType.CLOSE):
            print("CLOSING: {}".format(info["symbols"]))
            for symbol in info["symbols"]:
                symbol_open[symbol] = False
            has_open = False
            for symbol, status in symbol_open.items():
                if status == True:
                    has_open = True
            if not has_open:
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
                return
        elif info_type == str(InfoType.ERROR):
            print("ERROR: {}".format(info["error"]))
        elif info_type == str(InfoType.TRADE):
            symbol_trade[info["symbol"]].append((info["price"], info["size"]))
        elif info_type == str(InfoType.ACK):
            _order_id = info["order_id"]
            if _order_id in orders:
                order = orders[_order_id]
                print("Order {}: Dir - {}, Symbol - {}, Price - {}, Orig - {} has been placed on the books"
                        .format(_order_id, order[0], order[1], order[2], order[3], order[4]))
            else:
                conversion = conversions[_order_id]
                print("Order {}: Dir - {}, Symbol - {}, Size - {} has been converted"
                        .format(_order_id, conversion[0], conversion[1], conversion[2]))
                if conversion[1] == str(Symbol.VALE):
                    symbol_positions[str(Symbol.VALE)] -= conversion[2]
                    symbol_positions[str(Symbol.VALBZ)] += conversion[2]
                    symbol_positions[str(Symbol.USD)] -= 10
                elif conversion[1] == str(Symbol.XLF):
                    symbol_positions[str(Symbol.USD)] -= 100
                    if conversion[0] == str(Direction.BUY):
                        symbol_positions[str(Symbol.BOND)] -= 3
                        symbol_positions[str(Symbol.GS)] -= 2
                        symbol_positions[str(Symbol.MS)] -= 3
                        symbol_positions[str(Symbol.WFC)] -= 2
                        symbol_positions[str(Symbol.XLF)] += 10
                    elif conversion[0] == str(Direction.SELL):
                        symbol_positions[str(Symbol.BOND)] += 3
                        symbol_positions[str(Symbol.GS)] += 2
                        symbol_positions[str(Symbol.MS)] += 3
                        symbol_positions[str(Symbol.WFC)] += 2
                        symbol_positions[str(Symbol.XLF)] -= 10

                print("CURRENT POSITION: {}".format(symbol_positions))

        elif info_type == str(InfoType.FILL):
            _order_id = info["order_id"]
            order = orders[_order_id]
            price = order[2]
            size = info["size"]

            orders[_order_id] = (order[0], order[1], order[2], order[3], order[4] - size)
            order = orders[_order_id]

            print("Order {}: Dir - {}, Symbol - {}, Price - {}, Orig - {}, Current - {} has been filled"
                    .format(_order_id, order[0], order[1], order[2], order[3], order[4]))

            if order[0] == str(Direction.SELL):
                symbol_positions[str(Symbol.USD)] += (price * size)
                symbol_positions[str(order[1])] -= size
            else:
                symbol_positions[str(order[1])] += size
            print("CURRENT POSITION: {}".format(symbol_positions))

        elif info_type == str(InfoType.OUT):
            _order_id = info["order_id"]
            order = orders[_order_id]
            print("Order {}: Dir - {}, Symbol - {}, Price - {}, Orig - {}, Current - {} is off the books"
                    .format(_order_id, order[0], order[1], order[2], order[3], order[4]))

        elif info_type == str(InfoType.BOOK):
            symbol = info["symbol"]
            buy = info["buy"]
            sell = info["sell"]
            symbol_book[symbol] = { "BUY": buy, "SELL": sell }