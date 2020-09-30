import yfinance as yf
import pandas as pd
from yfinance import ticker

def get_statement(ticker):
    stock = yf.Ticker(ticker)
    financials = stock.financials
    balance_sheet = stock.balance_sheet
    pd.set_option('display.float_format', lambda x: '%.3f' % x)
    return financials, balance_sheet

if __name__ == "__main__":
    tickers = ['F', 'BKNG']
    for ticker in tickers:
        financials, balance_sheet = get_statement(ticker)

        frames = [financials, balance_sheet]
        data = pd.concat(frames)
        depreciation_F= {
            "2019-12-31": -31020000,
            "2018-12-31": -30243000,
            "2017-12-31": -29862000,
            "2016-12-31": -27804000
        }

        depreciation_BKNG= {
            "2019-12-31": -927000,
            "2018-12-31": -693000,
            "2017-12-31": -543417,
            "2016-12-31": -358970
        }
        # print(data)
        for year in list(data):
            year_str = year.strftime("%Y-%m-%d")
            interest_after_tax = data.loc['Income Before Tax', year] - data.loc['Income Tax Expense', year]
            net_income = data.loc['Income Before Tax', year]
            total_capital = data.loc['Long Term Debt', year] + data.loc['Total Stockholder Equity', year]
            equity = data.loc['Total Stockholder Equity', year]
            sales = data.loc['Total Revenue', year]
            total_assets = data.loc['Total Assets', year]
            receivables = data.loc['Net Receivables', year]
            avg_daily_sales = sales / 365
            long_term_debt = data.loc['Long Term Debt', year]
            total_liabilities = data.loc['Total Liab', year]
            Ebit = data.loc['Ebit', year]
            if ticker == 'F':
                depreciation = depreciation_F[year_str]
            if ticker == 'BKNG':
                depreciation = depreciation_BKNG[year_str]
            interest_payments = data.loc['Interest Expense', year]
            current_liabilities = data.loc['Total Current Liabilities', year]
            marketable_securities = data.loc['Short Term Investments', year]
            cash = data.loc['Cash', year]
            current_assets = data.loc['Total Current Assets', year]

            # return_on_assets : asset_turnover * operating_profit_margin
            ratios = {
                "return on capital": (interest_after_tax + net_income) / total_capital,
                "return on equity" : net_income / equity,
                "asset turnover" : sales / total_assets,
                "average collection_period" : receivables / avg_daily_sales,
                "profit margin" : net_income / sales,
                "operating profit_margin" : (interest_after_tax + net_income) / sales,
                "return on assets" : (interest_after_tax + net_income) / total_assets,
                "long term debt ratio" : long_term_debt / (long_term_debt + equity),
                "long term debt equity ratio" : long_term_debt / equity,
                "total debt ratio" : total_liabilities / total_assets,
                "cash coverage" : (Ebit + depreciation) / interest_payments,
                "current ratio" : current_assets / current_liabilities,
                "cash ratio" : (cash + marketable_securities) / current_liabilities,
                "quick ratio" : (cash + marketable_securities + receivables) / current_liabilities,
            }
            print('-' * 30)
            print(ticker, year_str)
            for key in ratios:
                print(f"{key}: {ratios[key]}")
            