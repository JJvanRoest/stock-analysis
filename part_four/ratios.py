import yfinance as yf
import pandas as pd

stock = yf.Ticker('BP')
financials = stock.financials
pd.set_option('display.float_format', lambda x: '%.3f' % x)
print(financials)
