
from datetime import datetime, time
import alpaca_trade_api as tradeapi
import os
import boto3
from time import sleep

# TODO: weight the alerts
# ALL_ALERTS = [
#     {
#         'symbol': 'KODK',
#         'prof_precent': 0.88
#     },
#     {
#         'symbol': 'RKT',
#         'prof_precent': 0.76
#     }
# ]
TOTAL_NUMBER_OF_ALERTS = os.environ.get('TOTAL_NUMBER_OF_ALERTS', 5)
# profitability_weight = {
#     ''
# }


def has_position(api, ticker):
    positions = api.list_positions()
    return any([x for x in positions if x.symbol == ticker])


def close_positions(api, profitmax=500):
    positions = api.list_positions()
    closed = []
    for position in positions:
        if float(position.unrealized_pl) > 100 or float(position.unrealized_plpc) > 0.01:
            print("unrealized PL GAIN", position.symbol, position.unrealized_pl)
            api.close_position(position.symbol)
            close_symbol_orders(api, position.symbol)
            closed.append((position.symbol, float(position.unrealized_pl)))
        elif float(position.unrealized_pl) < -150 or float(position.unrealized_plpc) < -0.01:
            print("unrealized PL LOSS", position.symbol, position.unrealized_pl)            
            api.close_position(position.symbol)
            close_symbol_orders(api, position.symbol)
            closed.append((position.symbol, float(position.unrealized_pl)))
    return closed


def close_symbol_orders(api, symbol):
    orders = api.list_orders()
    closed = []
    for order in orders:
        if order.symbol == symbol:
            api.cancel_order(order.id)
            closed.append((order.symbol, order.id))
    return closed


def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else:  # crosses midnight
        return check_time >= begin_time or check_time <= end_time


def get_current_price(api, ticker):
    barset = api.get_barset(ticker, '5Min', limit=1)
    bars = barset[ticker]
    return bars[-1].c


def get_contracts(api, item, cash, num_alerts=TOTAL_NUMBER_OF_ALERTS):
    """
    get the cash on hand 
    """
    positions = api.list_positions()
    bottom = (num_alerts - len(positions) ) if num_alerts > len(positions) else 1
    avaible_fraction =  1/ bottom
    avaible_fraction = avaible_fraction * .8 if avaible_fraction >= 0.98 else avaible_fraction
    barset = api.get_barset(item.ticker, '5Min', limit=1)

    bars = barset[item.ticker]
    close = bars[-1].c
    amount_to_spend = cash / avaible_fraction
    contracts = int(amount_to_spend/close)
    print("close", close)
    print("contracts*close", contracts*close)
    return contracts


def is_during_hours(ticker):
    # testing out after hours
    # TODO: MR 1 only type="limit" is allowed for extended hours orders
    # return True
    # 9:30am and 4pm east coast
    return is_time_between(time(13, 30), time(20, 00))


def can_sell(item, api):
    during_hours = is_during_hours(item.ticker)
    return item.order == "sell" and during_hours


def log_transaction(item, contracts, error):
    # boto3.log
    print(item.ticker, contracts, error)


def get_api():
    key_id = os.environ.get('APCA_API_KEY_ID')
    secret = os.environ.get('APCA_API_SECRET_KEY')
    api = tradeapi.REST(key_id, secret, base_url=os.environ.get(
        'APCA_BASE_URL'))  # or use ENV Vars shown below
    return api


def handler(item, use_max_value=True):
    print("ITEM handler", item)
    print(item.order)
    can_trade = is_during_hours(item.ticker)
    api = get_api()
    account = api.get_account()

    contracts = abs(int(item.pos_size))
    try:
        if use_max_value:
            # use max of available cash
            contracts = get_contracts(api, item, float(account.cash))
    except Exception as e:
        print(e)

    if item.order == "buy" and can_trade:
        error = None
        price = get_current_price(api, item.ticker)
        try:            
            closed = close_symbol_orders(api, item.ticker)
            sleep(0.1)
            if has_position(api, item.ticker):
                res1 = api.close_position(item.ticker)
                            
                print("CLOSE ", item.ticker, contracts, closed)       
                sleep(0.5)
            
            # res = api.submit_order(
            #     symbol=item.ticker,
            #     side=item.order,
            #     type='market',
            #     qty=contracts,
            #     time_in_force='day'
            # )
            res = api.submit_order(
                symbol=item.ticker,
                side=item.order,
                type='market',
                qty=contracts,
                order_class='bracket',
                time_in_force='day',
                stop_loss={'stop_price': price * 0.95,
                           'limit_price':  price * 0.94},
                take_profit={'limit_price': price * 1.05}
            )
            print("BUY ", res.symbol, contracts)
        except Exception as e:
            error = e

        log_transaction(item, contracts, error)

    elif item.order == "sell" and can_trade:
        error = None

        try:
            closed = close_symbol_orders(api, item.ticker)
            sleep(0.1)
            if has_position(api, item.ticker):                
                res1 = api.close_position(item.ticker)         
                print("CLOSE ", item.ticker, contracts, closed) 
                sleep(0.5)

            # res = api.submit_order(
            #     symbol=item.ticker,
            #     side=item.order,
            #     type='market',
            #     qty=contracts,
            #     time_in_force='day'
            # )
            price = get_current_price(api, item.ticker)
            res = api.submit_order(
                symbol=item.ticker,
                side=item.order,
                type='market',
                qty=contracts,
                time_in_force='day',
                order_class='bracket',
                stop_loss={'stop_price': price * 1.04,
                           'limit_price':  price * 1.05},
                take_profit={'limit_price': price * 0.95}
            )

            print("SELL ", res.symbol, contracts)
        except Exception as e:
            error = e
        log_transaction(item, contracts, error)

    close_positions(api)
    # api.cancel_all_orders() # remove open orders
    account = api.get_account()
    return account.cash

# if __name__ == "__main__":
    # handler()

# TODO: send kill all order transactions before after hours
