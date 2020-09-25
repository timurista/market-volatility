import requests
import json
from src.alpaca import get_api, get_current_price
from time import sleep

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
        data['order'] = "buy"
        data['pos_size'] = 39
        data['price'] = price
        print(requests.post("https://timurista-personal-web-tasks.herokuapp.com/api/execute_alpaca_trade", json=data).content)

if __name__ == "__main__":
    main()

