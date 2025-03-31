from init import TushareWrapper
from stock_utils import StockUtils
from trader_utils import TraderUtils
import pandas as pd
import yaml

# Load config
with open('config.yaml') as f:
    config = yaml.safe_load(f)

# Initialize
wrapper = TushareWrapper()
utils = StockUtils()
trader = TraderUtils(config)

# Get daily data
daily = wrapper.query('daily', ts_code='601318.SH', start_date='20190101', end_date='20201231')
daily['trade_date'] = pd.to_datetime(daily['trade_date'])
daily.set_index('trade_date', inplace=True)

# Generate signals
daily['MA5'] = utils.calculate_moving_average(daily['close'], 5)
daily['MA20'] = utils.calculate_moving_average(daily['close'], 20)
daily['Signal'] = 0
daily.loc[daily['MA5'] > daily['MA20'], 'Signal'] = 1  # Buy signal
daily.loc[daily['MA5'] <= daily['MA20'], 'Signal'] = -1  # Sell signal

print("Trading Signals:")
print(daily[['close', 'MA5', 'MA20', 'Signal']].tail(10))