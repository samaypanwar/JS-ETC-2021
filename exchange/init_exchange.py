from socket import *
from socket import error as socket_error
from utils.hyperparameters import *
from data import *
from typing import Any, BinaryIO, Dict
from utils.data_types import *
import json
import time

########################
## EXCHANGE FUNCTIONS ##
########################

def create_exchange() -> BinaryIO:
    global SERVER_STATUS
    sock = socket(AF_INET, SOCK_STREAM)
    print("Connecting to the server now...")
    sock.connect((EXCHANGE_HOSTNAME, PORT))
    print("Connected.")
    SERVER_STATUS = 1
    print()
    return sock.makefile("rw", 1)

def recreate_exchange() -> BinaryIO:
    global SERVER_STATUS
    global ORDER_ID
    print("Reconnecting to server now...")
    attempts = 0
    while SERVER_STATUS == 0 and attempts < 20:
        try:
            attempts += 1
            exchange = create_exchange()
            SERVER_STATUS = 1
            write_to_exchange(exchange, HELLO)
            response = read_from_exchange(exchange)
            print(response)
            if response["type"] == str(InfoType.HELLO):
                SERVER_STATUS = 1
                print("POSITIONS: {}".format(response["symbols"]))
                symbols = response["symbols"]
                for symbol in symbols:
                    symbol_positions[symbol["symbol"]] = symbol["position"]
                print("Reconnected!")
                ORDER_ID = 0
                return exchange
            elif response["type"] == str(InfoType.OPEN):
                print("OPENING: {}".format(response["symbols"]))
                for symbol in response["symbols"]:
                    symbol_open[symbol] = True
                return exchange
            else:
                time.sleep(0.1)
                SERVER_STATUS = 0
        except socket_error:
            print("Failed to reconnect, trying again...")
            time.sleep(0.1)

def write_to_exchange(exchange: BinaryIO, obj: Any) -> None:
    json.dump(obj, exchange)
    exchange.write("\n")

def read_from_exchange(exchange: BinaryIO) -> Any:
    return json.loads(exchange.readline())
