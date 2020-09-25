import requests
import json
from src.alpaca import get_api, get_current_price
from time import sleep


def main():
    data = None
    api = get_api()

    with open('test.json') as json_file:
        data = json.load(json_file)
        price = get_current_price(api, 'TSLA')
        data['price'] = price
        print(requests.post("http://localhost:8000/api/execute_alpaca_trade", json=data).content)

    with open('test2.json') as json_file:
        data = json.load(json_file)
        price = get_current_price(api, 'FB')
        data['price'] = price
        print(requests.post("http://localhost:8000/api/execute_alpaca_trade", json=data).content)

if __name__ == "__main__":
    main()
