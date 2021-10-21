def trade_symbol(order_type, symbol, direction, price, size):

    return {
        'type': str(order_type),
        'symbol': symbol,
        'dir': direction,
        'price': price,
        'size': size
    }