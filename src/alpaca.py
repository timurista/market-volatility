
import alpaca_trade_api as tradeapi
import os

def handler(item):
    print("ITEM handler", item)
    print(item.order)
    key_id=os.environ.get('APCA_API_KEY_ID')
    secret=os.environ.get('APCA_API_SECRET_KEY')
    api = tradeapi.REST(key_id, secret, base_url=os.environ.get('APCA_BASE_URL')) # or use ENV Vars shown below


    if (item.order == "buy"):
        print("BUY ",item.ticker)

        api.submit_order(
            symbol=item.ticker,
            side=item.order,
            type='market',
            qty=item.contracts,
            time_in_force='day'
        )
    elif (item.order == "sell"):
        print("SELL ",item.ticker)
        api.submit_order(
            symbol=item.ticker,
            side=item.order,
            type='market',
            qty=item.contracts,
            time_in_force='day'
        )
    
    account = api.get_account()
    positions = api.list_positions()
    print(account)
    return account.cash

if __name__ == "__main__":
    handler()
