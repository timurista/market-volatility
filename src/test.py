from alpaca import get_api, get_contracts, has_position, close_profitable_positions
import json
from pydantic import BaseModel
import os

class Item(BaseModel):
    name: str
    order: str
    contracts: float
    pos_size: float
    ticker: str
    api_key: str


item = Item(**{
    "name":"Open Close Cross Strategy R5.1 revised by JustUncleL (3, SMMA, 8, 6, 0.85, 0, BOTH, 0, 0, 10000)", 
    "order": "buy",
    "contracts":"1",
    "ticker":"MR", 
    "pos_size":"39",
    "api_key": os.environ.get('SECRET_ETRADE_TOKEN')
})

def test_close_positions():
    api = get_api()
    closed = close_profitable_positions(api, 500)
    print("closed", closed)


def test_get_contracts():
    api = get_api()
    contracts = get_contracts(api, item, 10000)
    print(contracts)    

def test_get_contracts_100k():
    api = get_api()
    contracts = get_contracts(api, item, 100000)
    print(contracts)

def test_get_contracts_100k_no_postions():
    api = get_api()
    contracts = get_contracts(api, item, 100000, 0)
    print(contracts)

def test_has_position():
    api = get_api()
    print(has_position(api, 'MR'))

def test_can_trade():
    api = get_api()
    print(has_position(api, 'MR'))

if __name__ == "__main__":
    test_close_positions()
    test_get_contracts()
    test_get_contracts_100k()
    test_has_position()
