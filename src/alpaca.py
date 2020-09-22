
import alpaca_trade_api as tradeapi
import os

TOTAL_NUMBER_OF_ALERTS = os.environ.get('TOTAL_NUMBER_OF_ALERTS', 2)

from datetime import datetime, time

key_id = os.environ.get('APCA_API_KEY_ID')
secret = os.environ.get('APCA_API_SECRET_KEY')
api = tradeapi.REST(key_id, secret, base_url=os.environ.get('APCA_BASE_URL'))  # or use ENV Vars shown below

def does_hold_position(api, ticker):
    positions = api.list_positions()
    return any([x for x in positions if x.symbol == ticker])


def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time

def get_contracts(api, item, cash, num_alerts=TOTAL_NUMBER_OF_ALERTS):
    """
    get the cash on hand 
    """
    positions = api.list_positions()
    avaible_fraction = num_alerts / len(positions) if len(positions) > 0 else 1
    barset = api.get_barset(item.ticker, '5Min', limit=1)

    bars = barset[item.ticker]
    close = bars[-1].c
    amount_to_spend = cash / avaible_fraction
    contracts = int(amount_to_spend/close)
    print("close", close)
    print("contracts*close", contracts*close)
    return contracts

def is_during_hours():
    return is_time_between(time(13,30), time(23,00))

def can_sell(item, api):
    during_hours = is_during_hours()
    hold_position = does_hold_position(api, item.ticker)
    return item.order == "sell" and during_hours and hold_position

def handler(item):
    print("ITEM handler", item)
    print(item.order)
    account = api.get_account()
    
    # use max of available cash
    contracts = 1
    try:
        contracts = get_contracts(api, item, float(account.cash))
    except Exception as e:
        print(e)

    if item.order == "buy" and is_during_hours():
        res = api.submit_order(
            symbol=item.ticker,
            side=item.order,
            type='market',
            qty=item.contracts,
            time_in_force='day'
        )
        print("SELL ", item, res)
    elif item.order == "sell" and can_sell(item, api):
        res = api.submit_order(
            symbol=item.ticker,
            side=item.order,
            type='market',
            qty=item.contracts,
            time_in_force='day'
        )
        print("SELL ", item, res)

    account = api.get_account()
    positions = api.list_positions()
    return account.cash

# if __name__ == "__main__":
    # handler()

# TODO: send kill all order transactions before after hours
