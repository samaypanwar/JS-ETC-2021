from data import orderbook, executed_trades, currently_open_symbols
from strategy.trades import trade_symbol
from utils.data_types import Ticker, Action, Direction

def adr_strategy():

    global executed_trades, orderbook

    if currently_open_symbols[Ticker.VALBZ] == False or currently_open_symbols[Ticker.VALE] == False: return []

    vale_trade_prices = list(map(lambda x: x[0], executed_trades[Ticker.VALE]))
    valbz_trade_prices = list(map(lambda x: x[0], executed_trades[Ticker.VALE]))

    if len(vale_trade_prices) >= 10 and len(valbz_trade_prices) >= 10:
        vale = vale_trade_prices[-10:]
        valbz = valbz_trade_prices[-10:]
        result = adr_signal(valbz, vale)

        if result:
            adr_mean = result[0] + 1
            cs_mean = result[1] - 1
            buy_vale = trade_symbol(Action.ADD, Ticker.VALE, Direction.BUY, price=adr_mean , size=10)
            convert_to_valbz = trade_symbol(Action.CONVERT, Ticker.VALE, Direction.SELL, size=10)
            sell_valbz = trade_symbol(Action.ADD, Ticker.VALBZ, Direction.SELL, price=cs_mean , size=10)

            trades = buy_vale + convert_to_valbz + sell_valbz

            return trades

    return []

def adr_signal(cs_trade_prices, adr_trade_prices):

    mean = lambda x: sum(x) / len(x)

    cs_mean = mean(cs_trade_prices)
    adr_mean= mean(adr_trade_prices)
    fair_diff = cs_mean - adr_mean

    if (fair_diff >= 3):
        print("CS_MEAN: {} ADR_MEAN: {}".format(cs_mean, adr_mean))
        return [adr_mean, cs_mean]

    return None