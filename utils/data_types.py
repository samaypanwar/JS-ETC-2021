class Action:
  ADD: str = "add"
  CONVERT: str = "convert"

class Ticker:
  BOND: str = "BOND"
  GS: str = "GS"
  MS: str = "MS"
  USD: str = "USD"
  VALBZ: str = "VALBZ"
  VALE: str = "VALE"
  WFC: str = "WFC"
  XLF: str = "XLF"

class Direction:
  BUY: str = "BUY"
  SELL: str = "SELL"

class ResponseType:
  HELLO: str = "hello"
  OPEN: str = "open"
  CLOSE: str = "close"
  ERROR: str = "error"
  BOOK: str = "book"
  TRADE: str = "trade"
  ACK: str = "ack"
  REJECT: str = "reject"
  FILL: str = "fill"
  OUT: str = "out"