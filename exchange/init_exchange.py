from socket import *
from socket import error as SOCKET_ERROR
from utils.hyperparameters import *
from data import *
from typing import BinaryIO
from utils.data_types import *
import time
from communicate import read_from_exchange, write_to_exchange

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
    global ORDER_ID
    print("Reconnecting to server now...")

    # Making a counter for the attempts for reconnection
    attempts = 0
    # While not connected to server and you have tried less than 20 times
    while SERVER_STATUS == 0 and attempts < 20:
        try:
            attempts += 1
            # Try creating an exchange
            exchange = create_exchange()
            SERVER_STATUS = 1
            # Test the connection by sending a HELLO - command from the hyperparameters.py file
            write_to_exchange(exchange, HELLO)
            # Read the response from the server
            response = read_from_exchange(exchange)
            # IT is probably a JSON object as a dictionary
            print(response)
            # If the type of response is 'hello'
            if response["type"] == str(InfoType.HELLO):
                # Say that we are connected successfully
                SERVER_STATUS = 1
                # The response 'symbols' key contains each symbol and your position in that symbol
                print("POSITIONS: {}".format(response["symbols"]))
                # Then to record our current position, add your current position to our symbol position dictionary
                # which records all our current positions
                all_symbols = response["symbols"]
                for ticker in all_symbols:
                    current_positions_in_symbols[ticker["symbol"]] = ticker["position"]
                print("Reconnected!")
                ORDER_ID = 0

                # Return the binary buffer object that is created from create_exchange()
                return exchange

            # However, if the response of the server is that the market is 'open'
            elif response["type"] == str(InfoType.OPEN):

                # Mark the symbols which are open as True in our symbol_open dictioanry
                print("OPENING: {}".format(response["symbols"]))
                for symbol in response["symbols"]:
                    currently_open_symbols[symbol] = True

                # Return the binary buffer object that is created from create_exchange()
                return exchange

            else:
                # If the response is neither 'open' nor 'hello' from the server, sleep and try again and
                # set server status to 0
                time.sleep(0.1)
                SERVER_STATUS = 0

        # If the socket returns an error, try again as well
        except SOCKET_ERROR:
            print(f"Attempt {attempts}: Failed to reconnect, trying again...")
            time.sleep(0.1)