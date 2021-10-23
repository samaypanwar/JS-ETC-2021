###########################
## CONSTANT DECLARATIONS ##
###########################

TEAM_NAME = "Wildcard"
TEST_ENV = "test"
ENV = TEST_ENV
TEST_EXCHANGE_INDEX = 0
PORT = 25000 + (TEST_EXCHANGE_INDEX if ENV == TEST_ENV else 0)
ZEROETH_HOSTNAME = "0-prod-like"
FIRST_HOSTNAME = "1-slower"
SECOND_HOSTNAME = "2-empty"
# EXCHANGE_HOSTNAME = "test-exch-" + TEAM_NAME.lower() + " " + str(PORT) if(ENV==TEST_ENV) else PROD_ENV
EXCHANGE_HOSTNAME = '1.1.1.1' #'10.0.251.221'

HELLO = { "type": "hello", "team": TEAM_NAME.upper() }

#################################
## MAIN DATA / DATA STRUCTURES ##
#################################

SERVER_STATUS = 1
ORDER_ID = 0

BOND_FAIR_VALUE = 1000
LARGE_NUMBER = 10000000000