import requests
import json


def main():
    data = None
    with open('test.json') as json_file:
        data = json.load(json_file)
        print(requests.post("http://localhost:8000/api/execute_alpaca_trade", json=data).content)

    with open('test2.json') as json_file:
        data = json.load(json_file)
        print(requests.post("http://localhost:8000/api/execute_alpaca_trade", json=data).content)

if __name__ == "__main__":
    main()
