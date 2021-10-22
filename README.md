# JS-ETC-2021
jas kim and I gonna win some

// returns your positions, record our current positions in current_positions_in_symbols
{ type: 'HELLO', symbols: [ { symbol: str, position: int } ] }

// returns stocks open for trading, mark them true in currently_open_symbols
{ type: 'OPEN', symbols: [ str ] }

// returns stocks closed for trading, mark them false in currently_open_symbols
{ type: 'CLOSE', symbols: [ str ] }

// returns an error, no need to do anything
{ type: 'ERROR', error: str }

// returns price and size of a trade that has been executed in the market, add trade information to symbol_trade
{ type: 'TRADE', symbol: str, price: int, size: int }

// returns id of the order which has been added to the books, do nothing if it is a regular trade order else it is a conversion so adjust positions and deduct conversion cost
{ type: 'ACK', order_id: int }

// returns order id and the size of the trade (partial fills allowed), update positions and increment cash balance if sell order (gotta pay upfront for buy order)
{ type: 'FILL', order_id: int, size: int }

// returns the order id which has been removed form the books (when can it be removed?)
{ type: 'OUT', order_id: int }

// returns the book with a symbol and buy and sell price (what are these values?), update in symbol_book
{ type: 'BOOK', symbol: str, buy: int, sell: int }