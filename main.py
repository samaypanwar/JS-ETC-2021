from strategy.trades import execute_strategy
from utils.hyperparameters import *
from data import *
from utils.data_types import *
from exchange.init_exchange import *
from exchange.communicate import *
from exchange.exchange_info import *
import argparse

####################
## MISC FUNCTIONS ##
####################

def initialize() -> None:
    print("Initialising...")
    print("Environment: {}".format(ENV))
    print("Port: {}".format(PORT))
    print("Hostname: {}".format(EXCHANGE_HOSTNAME))
    print()

def check_argv():

    parser = argparse.ArgumentParser()
    parser.add_argument('mode', type=str, nargs=1,
                        default='1,1,1,1')

    return parser.parse_args()

def main() -> None:

    args = check_argv()
    mode = list(map(int, args.mode.split(sep=',')))
    global SERVER_STATUS
    exchange: BinaryIO = create_exchange()
    print("Exchange successfully initialised")
    write_to_exchange(exchange, HELLO)
    while True:
        server_response(exchange)
        if SERVER_STATUS == 1:
            execute_strategy(exchange, mode=mode)
            time.sleep(0.1)
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