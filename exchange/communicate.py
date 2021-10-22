import json
from typing import BinaryIO, Any

def read_from_exchange(exchange: BinaryIO):
    return json.loads(exchange.readline())

def write_to_exchange(exchange: BinaryIO, obj: Any) -> None:
    json.dump(obj, exchange)
    exchange.write("\n")