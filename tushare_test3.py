from init import TushareWrapper
import pandas as pd

# Initialize
wrapper = TushareWrapper()

# Get income statement
income = wrapper.query('income', ts_code='600519.SH', start_date='20190101', end_date='20201231')
income['end_date'] = pd.to_datetime(income['end_date'])
income.set_index('end_date', inplace=True)

# Get balance sheet
balancesheet = wrapper.query('balancesheet', ts_code='600519.SH', start_date='20190101', end_date='20201231')
balancesheet['end_date'] = pd.to_datetime(balancesheet['end_date'])
balancesheet.set_index('end_date', inplace=True)

# Get cash flow statement
cashflow = wrapper.query('cashflow', ts_code='600519.SH', start_date='20190101', end_date='20201231')
cashflow['end_date'] = pd.to_datetime(cashflow['end_date'])
cashflow.set_index('end_date', inplace=True)

print("Financial Statements for Kweichow Moutai (600519.SH):")
print("\nIncome Statement:")
print(income[['revenue', 'n_income']].tail())
print("\nBalance Sheet:")
print(balancesheet[['total_assets', 'total_liab']].tail())
print("\nCash Flow:")
print(cashflow[['n_cashflow_act', 'n_cashflow_inv_act']].tail())