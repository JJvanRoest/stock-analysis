import requests
import numpy as np
import datetime
import yfinance as yf
import json
from pandas import DataFrame
import statsmodels.api as sm
from statsmodels import regression
import matplotlib.pyplot as plt


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
    history = stock.history(period='5y', interval = '1mo')
    history.sort_index(ascending=False, inplace=True)
    print(history.dropna(axis='rows'))
    print(history.Close.tolist())

    history_json = history.to_json()
    write_json_file(history_json, f'yahoo_data_{ticker}')

    yf_info = stock.info
    json_info = json.dumps(yf_info)
    write_json_file(json_info, f'yahoo_info_{ticker}')
    
    history = history.dropna(axis='rows')

    # return history.Close.pct_change()[1:]
    return history.Close.pct_change()[1:].tolist()

def beta_calculation_OLS(x, y):
    # Using linear regression model
    # Beta = covariance(x,y) / variance(x)
    x = sm.add_constant(x)
    model = regression.linear_model.OLS(y,x).fit()

    # x = x[:, 1]
    # return model.params[0], model.params[1]
    beta = model.params[1]
    return str(beta)

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
    cov = counter / len(stock)

    return cov

def r_squared_calc(stock, market):
    correlation_matrix = np.corrcoef(stock, market)
    correlation_xy = correlation_matrix[0,1]
    r_squared = correlation_xy**2
    return r_squared


def CAPM_calculation():
    ER_i     # Expected return of investment
    R_f # Risk-free rate
    Beta_i # Beta of investment
    ER_m # Expected return of market
    
    ER_i = R_f + Beta_i * (ER_m - R_f)

    return ER_i


def price_dividend():
    P_0 = 0
    DIV_1 = 0
    r = 0
    g = 0

    # P_0 = DIV_1 / (r - g)

    # return P_0

    g = -(DIV_1 / P_0) + r
    return g

def price_eps():
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


if __name__ == "__main__":
    global save_data
    
    save_data = True
    plot = False

    stock_name = 'AAPL'

    stock = yahoo_fin(stock_name)
    gspc = yahoo_fin('^GSPC')
    print(beta_calculation_OLS(gspc, stock))
    print(beta_calculation_np(stock, gspc))
    print(beta_calculation(stock, gspc))
    print(r_squared_calc(stock, gspc))

    print('---------------------------')


    if plot:
        plt.figure(figsize=(20,10))
        stock.plot()
        gspc.plot()
        plt.ylabel("Daily return of f'{stock_name}' and GSPC")
        plt.show()


    # goog = [1551.36, 1591.04, 1634.18, 1482.96, 1413.61, 1428.92, 1348.66, 1162.81, 1339.33, 1434.23, 1337.02, 1304.96, 1260.11, 1219.0, 1188.1, 1216.68, 1080.91, 1103.63, 1188.48, 1173.31, 1119.92, 1116.37, 1035.61, 1094.43, 1076.77, 1193.47, 1218.19, 1217.26, 1115.65, 1084.99, 1017.33, 1031.79, 1104.73, 1169.94, 1046.4, 1021.41, 1016.64, 959.11, 939.33, 930.5, 908.73, 964.86, 905.96, 829.56, 823.21, 796.79, 771.82, 758.04, 784.54, 777.29, 767.05, 768.79, 692.1, 735.72, 693.01, 744.95, 697.77, 742.95, 758.88, 742.6, 710.81]

    # gspc = [3359.51, 3426.96, 3500.31, 3271.12, 3100.29, 3044.31, 2912.43, 2584.59, 2954.22, 3225.52, 3230.78, 3140.98, 3037.56, 2976.74, 2926.46, 2980.38, 2941.76, 2752.06, 2945.83, 2834.4, 2784.49, 2704.1, 2506.85, 2760.17, 2711.74, 2913.98, 2901.52, 2816.29, 2718.37, 2705.27, 2648.05, 2640.87, 2713.83, 2823.81, 2673.61, 2584.84, 2575.26, 2519.36, 2471.65, 2470.3, 2423.41, 2411.8, 2384.2, 2362.72, 2363.64, 2278.87, 2238.83, 2198.81, 2126.15, 2168.27, 2170.95, 2173.6, 2098.86, 2096.95, 2065.3, 2059.74, 1932.23, 1940.24, 2043.94, 2080.41, 2079.36]

    # print(beta_calculation_np(goog, gspc))
    # print(beta_calculation(goog, gspc))


    # alpha_vantage(ticker)



# https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=IBM&outputsize=full&apikey=demo