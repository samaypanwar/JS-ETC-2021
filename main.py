from strategy import execute_strategy
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

    args = check_argv()
    PROD_ENV = args.server
    
    if PROD_ENV == "production":
        EXCHANGE_HOSTNAME = '1.1.1.1'
    elif PROD_ENV == "test":
        EXCHANGE_HOSTNAME = '10.0.251.221'

    print("Initialising...")
    print("Environment: {}".format(ENV))
    print("Port: {}".format(PORT))
    print("Hostname: {}".format(EXCHANGE_HOSTNAME))
    print()

    return EXCHANGE_HOSTNAME

def check_argv():

    parser = argparse.ArgumentParser()
    parser.add_argument('mode', type=str, nargs='?',
                        default='1,0,0,0')
    parser.add_argument('server', type=str, nargs='?',
                        default='test')

    return parser.parse_args()

def main(EXCHANGE_HOSTNAME) -> None:

    args = check_argv()
    mode = list(map(int, args.mode.split(sep=',')))

    global SERVER_STATUS
    exchange: BinaryIO = create_exchange(EXCHANGE_HOSTNAME)
    print("Exchange successfully initialised")
    write_to_exchange(exchange, HELLO)
    while True:
        server_response(exchange)
        if SERVER_STATUS == 1:
            execute_strategy(exchange, mode=mode)
            time.sleep(0.05)
        elif SERVER_STATUS == 0:
            exchange = recreate_exchange(EXCHANGE_HOSTNAME)
            if SERVER_STATUS == 0:
                break

if __name__ == '__main__':
    EXCHANGE_HOSTNAME = initialize()
    while True:
        try:
            main(EXCHANGE_HOSTNAME)
        except SOCKET_ERROR:
            print("\nERROR: Retrying the connection...\n")
            time.sleep(0.1)