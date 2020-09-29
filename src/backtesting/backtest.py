import alpaca_backtrader_api
import backtrader as bt
from datetime import datetime
import os

ALPACA_API_KEY = os.environ.get('ALPACA_API_KEY')
ALPACA_SECRET_KEY = os.environ.get('ALPACA_SECRET_KEY')
ALPACA_PAPER = True


class SmaCross(bt.SignalStrategy):
  def log(self, txt, dt=None):     
    dt = dt or self.datas[0].datetime.date(0)     
    print('%s, %s' % (dt.isoformat(), txt)) #Print date and close
  def __init__(self):
    sma1, sma2 = bt.ind.SMA(period=20), bt.ind.SMA(period=200)
    crossover = bt.ind.CrossOver(sma1, sma2)
    self.signal_add(bt.SIGNAL_LONG, crossover)


cerebro = bt.Cerebro()
cerebro.addstrategy(SmaCross)

store = alpaca_backtrader_api.AlpacaStore(
    key_id=ALPACA_API_KEY,
    secret_key=ALPACA_SECRET_KEY,
    paper=ALPACA_PAPER
)

if not ALPACA_PAPER:
  broker = store.getbroker()  # or just alpaca_backtrader_api.AlpacaBroker()
  cerebro.setbroker(broker)

DataFactory = store.getdata  # or use alpaca_backtrader_api.AlpacaData
data0 = DataFactory(dataname='TSLA', historical=True, fromdate=datetime(
    2020, 9, 20), timeframe=bt.TimeFrame.Minutes)
cerebro.adddata(data0)

print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
cerebro.run()
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
cerebro.plot()
