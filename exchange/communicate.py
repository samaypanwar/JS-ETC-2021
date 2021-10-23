import json
from typing import BinaryIO, Any

def read_from_exchange(exchange: BinaryIO):
    line = exchange.readline()

    try:
        return json.loads(line)
    except:
        return {'type':'pass'}

def write_to_exchange(exchange: BinaryIO, obj: Any) -> None:
    json.dump(obj, exchange)
    exchange.write("\n")