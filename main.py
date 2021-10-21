from utils.hyperparameters import *
from data import *
from utils.data_types import *
from exchange.init_exchange import *
from exchange.communicate import *
from exchange.exchange_info import *

####################
## MISC FUNCTIONS ##
####################

def initialize() -> None:
    print("Initialising...")
    print("Environment: {}".format(ENV))
    print("Port: {}".format(PORT))
    print("Hostname: {}".format(EXCHANGE_HOSTNAME))
    print()

def main() -> None:
    global SERVER_STATUS
    exchange: BinaryIO = create_exchange()
    print("Exchange successfully initialised")
    write_to_exchange(exchange, HELLO)
    while True:
        server_info(exchange)
        if SERVER_STATUS == 1:
            # do_action(exchange)
            pass
        elif SERVER_STATUS == 0:
            exchange = recreate_exchange()
            if SERVER_STATUS == 0:
                break

if __name__ == '__main__':
    initialize()
    while True:
        try:
            main()
        except SOCKET_ERROR:
            print("\nERROR: Retrying the connection...\n")
            time.sleep(0.1)