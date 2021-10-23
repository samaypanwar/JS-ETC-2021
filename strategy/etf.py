from data import orderbook, ETF_constituents
from strategy.trades import trade_symbol
from strategy.orderbook_filling import calculate_fair_value
from utils.data_types import Ticker, Direction, Action
from utils.hyperparameters import BOND_FAIR_VALUE

def etf_strategy():
    """Uses the more liquid basket items to evaluate XLF pricing, and returns a list of trades to make.

    If basket items sell < XLF buy, then we will buy the basket items, convert, and sell XLF. If the
        basket items buy > XLF sell, then we will buy XLF, convert, and sell the basket items.

    For all arguments, the format will be a dictionary with keys `BUY"` and `"SELL"`, and the values
        will be lists of resting orders.

    """

    global orderbook
    gs = orderbook[Ticker.GS]
    ms = orderbook[Ticker.MS]
    wfc = orderbook[Ticker.WFC]
    xlf = orderbook[Ticker.XLF]

    empty = _check_empty_books(gs, ms, wfc, xlf)
    if empty: return []

    if _calc_xlf_fair_value(gs, ms, wfc, Direction.SELL) + 34 < (xlf[Direction.BUY][0][0] * 10):

        trades = _execute_basket_items(gs, ms, wfc, Direction.BUY)
        convert_to_xlf = trade_symbol(Action.CONVERT, Ticker.XLF, Direction.BUY, size=30)
        sell_xlf = trade_symbol(Action.ADD, Ticker.XLF, Direction.SELL, price=xlf[Direction.BUY][0][0], size=30)

        trades.append(convert_to_xlf)
        trades.append(sell_xlf)

        return trades

    elif _calc_xlf_fair_value(gs, ms, wfc, Direction.BUY) > (xlf[Direction.SELL][0][0] * 10 + 34):

        buy_xlf = trade_symbol(Action.ADD, Ticker.XLF, Direction.BUY, price=xlf[Direction.SELL][0][0], size=30)
        convert_to_xlf = trade_symbol(Action.CONVERT, Ticker.XLF, Direction.SELL, size=30)
        trades = _execute_basket_items(gs, ms, wfc, Direction.BUY)

        trades.append(buy_xlf)
        trades.append(convert_to_xlf)

        return trades

    return []

def _check_empty_books(gs, ms, wfc, xlf):
    if not (gs and ms and wfc and xlf):
        return True

    for direction in [Direction.BUY, Direction.SELL]:
        if not (gs[direction] and ms[direction] and wfc[direction] and xlf[direction]):
            return True

    return False


def _calc_xlf_fair_value(gs, ms, wfc, direction):

    # If we want fairvalue instead of the top priority orderbook
    # gs_fairvalue = calculate_fair_value(Ticker.GS, trim=0.1, directional=True, direction=direction)
    # ms_fairvalue = calculate_fair_value(Ticker.GS, trim=0.1, directional=True, direction=direction)
    # wfc_fairvalue = calculate_fair_value(Ticker.GS, trim=0.1, directional=True, direction=direction)

    gs_fairvalue = gs[direction][0][0]
    ms_fairvalue = ms[direction][0][0]
    wfc_fairvalue = wfc[direction][0][0]

    xlf_fairvalue =  3*BOND_FAIR_VALUE + 2*gs_fairvalue + 3*ms_fairvalue + 2*wfc_fairvalue

    return xlf_fairvalue


def _execute_basket_items(gs, ms, wfc, direction):

    reverse_direction = Direction.BUY if direction == Direction.SELL else Direction.SELL
    trades = []
    for symbol, x in zip([gs, ms, wfc], [Ticker.GS, Ticker.MS, Ticker.WFC]):
        trade = trade_symbol(Action.ADD, symbol, direction, price=symbol[reverse_direction][0][0], size=3*ETF_constituents[x])

        trades.append(trade)

    return trades
