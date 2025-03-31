from init import TushareWrapper
from stock_utils import StockUtils
import pandas as pd

# Initialize
wrapper = TushareWrapper()
utils = StockUtils()

# Get daily data
daily = wrapper.query('daily', ts_code='600036.SH', start_date='20200101', end_date='20201231')
daily['trade_date'] = pd.to_datetime(daily['trade_date'])
daily.set_index('trade_date', inplace=True)

# Calculate technical indicators
daily['MA5'] = utils.calculate_moving_average(daily['close'], 5)
daily['MA20'] = utils.calculate_moving_average(daily['close'], 20)
daily['RSI14'] = utils.calculate_rsi(daily['close'], 14)

print("Technical Indicators:")
print(daily[['close', 'MA5', 'MA20', 'RSI14']].tail())