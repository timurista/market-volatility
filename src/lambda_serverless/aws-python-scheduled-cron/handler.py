import datetime
import logging
import os
import alpaca_trade_api as tradeapi

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_api():
    key_id = os.environ.get('APCA_API_KEY_ID')
    secret = os.environ.get('APCA_API_SECRET_KEY')
    api = tradeapi.REST(key_id, secret, base_url=os.environ.get('APCA_BASE_URL'))  # or use ENV Vars shown below
    return api

def close_profitable_positions(api, profitmax=500):
    positions = api.list_positions()
    closed = []
    for position in positions:
        if float(position.unrealized_pl) > 500 or float(position.unrealized_plpc) > 0.01:
            api.close_position(position.symbol)
            closed.append((position.symbol, float(position.unrealized_pl)))
    logger.log("closed positions ", closed)
    return closed

def run(event, context):
    current_time = datetime.datetime.now().time()
    name = context.function_name
    api = get_api()
    close_profitable_positions(api)
    logger.info("Your cron function " + name + " ran at " + str(current_time))
