from strategy.etf import etf_strategy
from utils.hyperparameters import ORDER_ID
from data import orderbook
from utils.data_types import Ticker
from strategy import penny_pinching
from strategy import orderbook_filling
from strategy.adr import adr_strategy
from strategy.trades import place_trade


def bonds_strategy():
    bond_trades = penny_pinching.trade_bonds(orderbook[Ticker.BOND])
    return bond_trades

def clear_orderbook():

    symbols = [Ticker.GS, Ticker.WFC, Ticker.MS]
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

    global ORDER_ID, orderbook

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