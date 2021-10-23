from utils.data_types import *
from utils.hyperparameters import *
from strategy import trade_symbol
from data import currently_open_symbols


def trade_bonds(bonds_orderbook):
    """Takes in an orderbook of the bonds and returns the list of buy and sell orders to submit to market by
    buying undervalued bonds (below 1000) and selling overvalued bonds (above 1000)

    Parameters
    ----------
    bonds_orderbook : List
        orderbook in the format: [buy_orders, sell_orders], where each element in the sublist is [price, quantity]

    Returns
    -------
    List[Trade]
        List of trades to execute
    """

    buy_trades = []
    sell_trades = []
    
    if currently_open_symbols[Ticker.BOND] == False: return []

    for price, size in bonds_orderbook["BUY"]:

        if price > BOND_FAIR_VALUE:
            trade = trade_symbol(Action.ADD, Ticker.BOND, Direction.SELL, price, size)
            buy_trades.append(trade)

    for price, size in bonds_orderbook["SELL"]:

        if price < BOND_FAIR_VALUE:
            trade = trade_symbol(Action.ADD, Ticker.BOND, Direction.BUY, price, size)
            sell_trades.append(trade)

    return buy_trades + sell_trades

