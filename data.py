## Order - has past orders and their sizes
orders = {}

## Conversions has past conversion related orders
conversions = {}

## Trade Prices that are metadata - (price, size)
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

## Book Prices - state of the orderbook currently if the market is open
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

## Open/Close Status of Symbols
currently_open_symbols = {
    "BOND": False,
    "GS": False,
    "MS": False,
    "USD": False,
    "VALBZ": False,
    "VALE": False,
    "WFC": False,
    "XLF": False
}

## Positions of Symbols that we currently hold in the market
current_positions_in_symbols = {
    "BOND": 0,
    "GS": 0,
    "MS": 0,
    "USD": 0,
    "VALBZ": 0,
    "VALE": 0,
    "WFC": 0,
    "XLF": 0
}

## Limits of Symbols - what is this for??
symbol_limits = {
    "BOND": 100,
    "GS": 100,
    "MS": 100,
    "VALBZ": 10,
    "VALE": 10,
    "WFC": 100,
    "XLF": 100
}

ETF_constituents = {
    'BOND': 3,
    'GS': 2,
    'MS': 3,
    'WFC': 2
        }