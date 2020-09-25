
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


def get_contracts(api, item, cash, use_max_value=False, num_alerts=TOTAL_NUMBER_OF_ALERTS):
    """
    get the cash on hand 
    """
    if not use_max_value:
        return abs(int(item.pos_size))
    positions = api.list_positions()
    bottom = (num_alerts - len(positions)
              ) if num_alerts > len(positions) else 1
    avaible_fraction = 1 / bottom
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
    return True
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

def get_oto_prices(price, orderType):
    diff = 0.01
    # "stop_loss": {
    #     "stop_price": "299",
    #     "limit_price": "298.5"
    # }
    if orderType == "buy":
        return price * (1-diff), price * (1-diff*1.2)
        # return (299, 298.5)
    elif orderType == "sell":
        return price * (1+diff), price * (1+diff*1.2)

# def get_oco_prices(price, orderType):


def get_prices(price, orderType):
    diff = 0.01
    # stop_loss_stop_price, stop_loss_limit_price,  take_profit_limit_price
    if orderType == "buy":
        return (price * (1-diff*1.2), price * (1-(diff)), price * (1-diff*1.5))
        # return (price * 0.95, price * 0.94, price * 1.05)
    elif orderType == "sell":
        return (price * (1+diff), price * (1+(diff)), price * (1+diff*1.5))
        # return (price * 1.04, price * 1.05, price * 0.95)


def submit_trade_w_brackets(api, item, contracts):
    error = None
    try:
        closed = close_symbol_orders(api, item.ticker)
        price = get_current_price(api, item.ticker)
        stop_loss_stop, stop_loss_limit = get_oto_prices(
            price, item.order)
        print(item.order, item.ticker, contracts, closed)
        print("stop_loss_stop", stop_loss_stop)
        print("stop_loss_limit", stop_loss_limit)
        # print("take_profit_limit", take_profit_limit)

        if has_position(api, item.ticker):   
            api.close_position(item.ticker)         
            # sleep(0.1)
            res = api.submit_order(
                symbol=item.ticker,
                side=item.order,
                type='market',
                # limit_price=item.price,
                qty=contracts*1,
                time_in_force='day',
                order_class='oto',
                stop_loss={'stop_price': stop_loss_stop,
                           'limit_price':  stop_loss_limit},
                # take_profit={'limit_price': take_profit_limit}
            )
            print(item.order, res.symbol, contracts)
        else:
            res = api.submit_order(
                symbol=item.ticker,
                side=item.order,
                type='market',
                qty=contracts,
                # limit_price=item.price,
                time_in_force='day',
                order_class='oto',
                stop_loss={'stop_price': stop_loss_stop,
                           'limit_price':  stop_loss_limit},
                # take_profit={'limit_price': take_profit_limit}
            )

            print(item.order, res.symbol, contracts)
    except Exception as e:
        error = e

    log_transaction(item, contracts, error)


def submit_trade_w_trail(api, item, contracts):
    error = None
    try:
        closed = close_symbol_orders(api, item.ticker)       
        price = get_current_price(api, item.ticker)
        trail_percent = 0.2

        if has_position(api, item.ticker):
            api.close_position(item.ticker)
            sleep(0.1)

        res1 = api.submit_order(
            symbol=item.ticker,
            side=item.order,
            type='market',
            qty=contracts,
            time_in_force='day'
        )
        sleep(0.2)

        res2 = api.submit_order(
            symbol=item.ticker,
            side="sell" if item.order == "buy" else "buy",
            type='trailing_stop',
            qty=contracts,
            time_in_force='day',
            trail_percent=trail_percent
        )

    except Exception as e:
        error = e

    log_transaction(item, contracts, error)


def submit_regular_trade(api, item, contracts):
    try:
        closed = close_symbol_orders(api, item.ticker)
        # sleep(0.1)
        if has_position(api, item.ticker):
            res1 = api.close_position(item.ticker)

            print(item.order, item.ticker, contracts, closed)
            sleep(0.1)
            res = api.submit_order(
                symbol=item.ticker,
                side=item.order,
                type='market',
                qty=contracts,
                time_in_force='day'
            )
        res = api.submit_order(
            symbol=item.ticker,
            side=item.order,
            type='market',
            qty=contracts,
            time_in_force='day'
        )

        print("BUY ", res.symbol, contracts)
    except Exception as e:
        error = e

    log_transaction(item, contracts, error)


def handler(item, use_max_value=False):
    print("ITEM handler", item)
    can_trade = is_during_hours(item.ticker)
    api = get_api()
    account = api.get_account()
    contracts = get_contracts(api, item, float(account.cash), use_max_value)
    # submit_trade_w_brackets(api, item, contracts)
    submit_trade_w_trail(api, item, contracts)

    # close_positions(api)
    # api.cancel_all_orders() # remove open orders
    account = api.get_account()
    return account.cash

# if __name__ == "__main__":
    # handler()

# TODO: send kill all order transactions before after hours
