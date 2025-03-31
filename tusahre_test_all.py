from init import TushareWrapper
import pandas as pd
import matplotlib.pyplot as plt

# Initialize
wrapper = TushareWrapper()

# 1. Get basic stock info
stock_basic = wrapper.query('stock_basic', list_status='L')
print(f"Total listed stocks: {len(stock_basic)}")

# 2. Get daily data for a stock
daily = wrapper.query('daily', ts_code='600519.SH', start_date='20200101', end_date='20201231')
daily['trade_date'] = pd.to_datetime(daily['trade_date'])
daily.set_index('trade_date', inplace=True)

# 3. Plot closing prices
daily['close'].plot(figsize=(12,6), title='Kweichow Moutai 2020 Daily Close')
plt.show()