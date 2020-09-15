import requests
import numpy as np
import datetime
import yfinance as yf
import json
from pandas import DataFrame
import statsmodels.api as sm
from statsmodels import regression
import matplotlib.pyplot as plt

import gui_start


def alpha_vantage(ticker):
    API_KEY = '0S3RCDO1A4TB4P0Y'
    URL = 'https://www.alphavantage.co'
    FUNCTION = 'TIME_SERIES_DAILY'

    OUTPUTSIZE = 'full'

    get_url = f'{URL}/query?function={FUNCTION}&symbol={ticker}&outputize={OUTPUTSIZE}&apikey={API_KEY}'

    req = requests.get(get_url)
    json = req.json()
    write_json_file(json, 'alphavant')


def yahoo_fin(ticker):
    stock = yf.Ticker(ticker)
    history = stock.history(period='3y', interval='1mo')
    history.sort_index(ascending=False, inplace=True)
    # print(history.dropna(axis='rows'))
    # print(history.Close.tolist())

    history_json = history.to_json()
    write_json_file(history_json, f'yahoo_data_{ticker}')

    stock_beta = 'NaN'
    try:
        yf_info = stock.info
        json_info = json.dumps(yf_info)
        write_json_file(json_info, f'yahoo_info_{ticker}')
        stock_beta = yf_info['beta']
    except Exception as e:
        print(e)
        pass

    history = history.dropna(axis='rows')

    # return history.Close.pct_change()[1:]
    return history.Close.pct_change()[1:].tolist(), stock_beta


def beta_calculation_OLS(x, y):
    # Using linear regression model
    # Beta = covariance(x,y) / variance(x)
    x = sm.add_constant(x)
    model = regression.linear_model.OLS(y, x).fit()
    # print(model.summary())
    # x = x[:, 1]
    return model.params[0], model.params[1], model.rsquared
    # beta = model.params[1]

    # return str(beta)


def beta_calculation_np(stock, market):
    cov_matr = np.cov(stock, market)
    variance = np.var(market)

    beta = cov_matr[0][1] / variance
    return beta


def beta_calculation(stock, market):
    cov = covariance_calc(stock, market)
    var = np.var(market)

    beta = cov / var

    return beta


def covariance_calc(stock, market):
    # Cov(x,y) = SUM [(xi - xm) * (yi - ym)] / (n - 1)
    counter = 0

    stock_avg = np.average(stock)
    market_avg = np.average(market)

    for i in range(len(stock)):
        counter += (stock[i] - stock_avg) * (market[i] - market_avg)
    cov = counter / (len(stock) - 1)

    return cov


def r_squared_calc(stock, market):
    correlation_matrix = np.corrcoef(stock, market)
    correlation_xy = correlation_matrix[0, 1]
    r_squared = correlation_xy**2
    return r_squared


def regression_plot(stock, market, alpha, beta, stock_name, market_name):
    x2 = np.linspace(stock.min(), stock.max(), 100)
    y_hat = x2 * beta + alpha

    plt.figure(figsize=(10, 8))
    plt.scatter(market, stock, alpha=0.3)
    plt.xlabel(f"{market_name} Monthly return")
    plt.ylabel(f"{stock_name} monthly return")
    plt.plot(x2, y_hat, 'r', alpha=0.7)


def CAPM_calculation():
    ER_i     # Expected return of investment
    R_f  # Risk-free rate
    Beta_i  # Beta of investment
    ER_m  # Expected return of market

    ER_i = R_f + Beta_i * (ER_m - R_f)

    return ER_i


def price_dividend():
    # Original formula P_0 = DIV_1 / (r - g)
    # Rewritten to return the growth factor

    P_0 = 0
    DIV_1 = 0
    r = 0
    g = 0

    # P_0 = DIV_1 / (r - g)

    # return P_0

    g = -(DIV_1 / P_0) + r
    return g


def price_eps():
    # Original formula P_0 = EPS_1 / r + PVGO
    # Rewritten to return the Present Value of Growth Opportunities

    P_0 = 0
    EPS_1 = 0
    r = 0
    PVGO = 0

    PVGO = -(EPS_1 / r) + P_0

    return PVGO

    # P_0 = EPS_1 / r + PVGO
    # return P_0


def write_json_file(data, source):
    global save_data
    if save_data:
        now = datetime.datetime.now()
        file_name = f'{now.hour}_{now.minute}_{now.second}_{source}.json'
        f = open(f'./json/{file_name}', "w")
        f.write(str(data))
        f.close()


def get_finance(stock_name, market_name):
    stock, beta_stock = yahoo_fin(stock_name)
    market, beta_null = yahoo_fin(market_name)
    print(f"{stock_name} & {market_name}")
    print(f"Beta (OLS): {beta_calculation_OLS(market, stock)[1]}")
    print(f"Beta (Cov Mat): {beta_calculation_np(stock, market)}")
    print(f"Beta (Bare): {beta_calculation(stock, market)}")
    print(f"Beta (Yahoo): {beta_stock}")
    print(f"R^2 (calculated): {r_squared_calc(stock, market)}")
    print(f"R^2 (OLS Regression): {beta_calculation_OLS(market, stock)[2]}")

    print('---------------------------')

    return stock, market


if __name__ == "__main__":
    global save_data

    save_data = True
    plot = True

    stock_names = ['F', 'TSLA', 'BKNG', 'EXPE']
    # market_name = '^GSPC'
    market_name = '^SP500TR'
    for stock_name in stock_names:
        stock, market = get_finance(stock_name, market_name)
    # stock = yahoo_fin(stock_name)
    # market = yahoo_fin(market_name)
    # print(beta_calculation_OLS(market, stock))
    # print(beta_calculation_np(stock, market))
    # print(beta_calculation(stock, market))
    # print(r_squared_calc(stock, market))

    # print('---------------------------')

        if plot:
            stock_arr = np.array(stock)
            market_arr = np.array(market)
            plt.figure(figsize=(20, 10))
            plt.plot(stock_arr)
            plt.plot(market_arr)
            plt.ylabel(f"Daily return of {stock_name} and {market_name}")

            file_name = datetime.datetime.now()
            plt.savefig(f"./plots/{file_name}.jpg")

            alpha, beta, rsquared = beta_calculation_OLS(market, stock)
            regression_plot(stock_arr, market_arr, alpha,
                            beta, stock_name, market_name)

            file_name = datetime.datetime.now()
            plt.savefig(f"./plots/{file_name}.jpg")

    # alpha_vantage(ticker)
