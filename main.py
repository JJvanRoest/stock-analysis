import requests
import numpy as np
import datetime
import yfinance as yf
import json
from pandas import DataFrame

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
    history = stock.history(period='1y')
    history.sort_index(ascending=False, inplace=True)
    print(history)
    history_json = history.to_json()
    write_json_file(history_json, f'yahoo_data_{ticker}')

    yf_info = stock.info
    json_info = json.dumps(yf_info)
    write_json_file(json_info, f'yahoo_info_{ticker}')


def write_json_file(data, source):
    now = datetime.datetime.now()
    file_name = f'{now.hour}_{now.minute}_{now.second}_{source}.json'
    f = open(f'./json/{file_name}', "w")
    f.write(str(data))
    f.close()


if __name__ == "__main__":
    ticker = 'AAPL'
    yahoo_fin(ticker)
    alpha_vantage(ticker)



# https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=IBM&outputsize=full&apikey=demo