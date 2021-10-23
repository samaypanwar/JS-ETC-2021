from socket import socket, error as SOCKET_ERROR, AF_INET, SOCK_STREAM
from utils.hyperparameters import PORT, HELLO, SERVER_STATUS, EXCHANGE_HOSTNAME
from data import currently_open_symbols, current_positions_in_symbols
from typing import BinaryIO
from utils.data_types import ResponseType
import time
from exchange.communicate import read_from_exchange, write_to_exchange
from exchange.exchange_info import handle_hello, handle_open


########################
## EXCHANGE FUNCTIONS ##
########################


def create_exchange() -> BinaryIO:
    """Creates an exchange by making a socket and a makefile,
    returns a binary buffer object related to the socket
    """
    # What is the current status of our server
    global SERVER_STATUS
    # Initiating a socket as a unique item from a family
    sock = socket(AF_INET, SOCK_STREAM)
    print("Connecting to the server now...")
    # Establish a connection with the server with the given port and IP
    sock.connect((EXCHANGE_HOSTNAME, PORT))
    print("Connected.")
    SERVER_STATUS = 1
    print()
    return sock.makefile("rw", 1)

def recreate_exchange() -> BinaryIO:
    """[summary]
    """

    # Checking the status of the server and the current order id
    global SERVER_STATUS
    print("Reconnecting to server now...")

    # While not connected to server and you have tried less than 20 times
    for attempt in range(20):

        try:
            # Try creating an exchange
            exchange = create_exchange()
            SERVER_STATUS = 1
            # Test the connection by sending a HELLO - command from the hyperparameters.py file
            write_to_exchange(exchange, HELLO)
            # Read the response from the server
            info = read_from_exchange(exchange)
            # IT is probably a JSON object as a dictionary
            print(info)
            # If the type of response is 'hello'
            if info["type"] == ResponseType.HELLO:
                handle_hello(info)
                # Return the binary buffer object that is created from create_exchange()
                return exchange

            # However, if the response of the server is that the market is 'open'
            elif info["type"] == ResponseType.OPEN:
                handle_open(info)
                # Return the binary buffer object that is created from create_exchange()
                return exchange

            else:
                # If the response is neither 'open' nor 'hello' from the server, sleep and try again and
                # set server status to 0
                time.sleep(0.1)
                SERVER_STATUS = 0

        # If the socket returns an error, try again as well
        except SOCKET_ERROR:
            print(f"Attempt {attempt}: Failed to reconnect, trying again...")
            time.sleep(0.1)