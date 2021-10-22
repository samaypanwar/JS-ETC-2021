from data import symbol_book, symbol_trade
from strategy import trade_symbol
from utils.data_types import Symbol, Action, Direction

def adr_strategy():

    global symbol_trade, symbol_book

    vale_trade_prices = list(map(lambda x: x[0], symbol_trade[Symbol.VALE]))
    valbz_trade_prices = list(map(lambda x: x[0], symbol_trade[Symbol.VALE]))

    if len(vale_trade_prices) >= 10 and len(valbz_trade_prices) >= 10:
        vale = vale_trade_prices[-10:]
        valbz = valbz_trade_prices[-10:]
        result = adr_signal(valbz, vale)

        if result:
            adr_mean = result[0] + 1
            cs_mean = result[1] - 1
            buy_vale = trade_symbol(Action.ADD, Symbol.VALE, Direction.BUY, price=adr_mean , size=10)
            convert_to_valbz = trade_symbol(Action.CONVERT, Symbol.VALE, Direction.SELL, size=10)
            sell_valbz = trade_symbol(Action.ADD, Symbol.VALBZ, Direction.SELL, price=cs_mean , size=10)

            trades = buy_vale + convert_to_valbz + sell_valbz

            return trades

    return []

# Common stock & its ADR pair trading strategy
def adr_signal(cs_trade_prices, adr_trade_prices):

    mean = lambda x: sum(x) / len(x)

    cs_mean: int = mean(cs_trade_prices)
    adr_mean: int = mean(adr_trade_prices)
    fair_diff: int = cs_mean - adr_mean

    if (fair_diff >= 2):
        return [adr_mean, cs_mean]

    return None