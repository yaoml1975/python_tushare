from init import TushareWrapper

# Initialize Tushare wrapper
wrapper = TushareWrapper()

# Example 1: Get basic stock information
stocks = wrapper.query('stock_basic', list_status='L')
print("Stock Basic Info:")
print(stocks.head())

# Example 2: Get daily trading data
daily = wrapper.query('daily', ts_code='000001.SZ', start_date='20210101', end_date='20210131')
print("\nDaily Data:")
print(daily.head())