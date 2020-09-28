import yfinance as yf
import matplotlib
from pandas import DataFrame
import matplotlib.pyplot as plt
import numpy as np
from datetime import date, timedelta


def get_data(tickers):
  tickers = yf.Tickers(tickers)
  return tickers

if __name__ == '__main__':
    tickers = ["BKNG", "F"]
    for ticker in tickers:
        time_deltas = [2, 0.5]
        for time_delta in time_deltas:
            days = time_delta * 365
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            df =  yf.download(ticker, start=start_date, end=end_date, interval='1d')
            df["Factor"] = df["Close"] / df["Adj Close"]
            print(df["Factor"].nunique(), df["Factor"].count())
            print(df['Adj Close'])
            daily_returns_current = []
            daily_returns_next = []
            scatter_coords = []
            for i in range(len(df['Adj Close'])):
                try:
                    next_day = df['Adj Close'][i+1]     # Used for day + 1
                    current_day = df['Adj Close'][i]
                    previous_day = df['Adj Close'][i-1]

                    daily_return_current = (current_day - previous_day) / previous_day * 100  # Calculate day coordinate
                    daily_returns_current.append(daily_return_current)

                    daily_return_next = (next_day - current_day) / current_day * 100   # Calculate day+1 coordinate
                    daily_returns_next.append(daily_return_next)
                except IndexError as e:
                    pass

            corr_matrix = np.corrcoef(daily_returns_next, daily_returns_current)
            corr = round(corr_matrix[0][1], 2)
            plt.scatter(daily_returns_current, daily_returns_next, s=10, alpha=1)
            axes = plt.gca()
            axes.set_xlim([-5,5])
            axes.set_ylim([-5,5])
            plt.suptitle(f'{ticker} (correlation: {corr})')
            plt.title(f"{start_date} to {end_date}, {time_delta} years")
            plt.xlabel("Return on day t, %")
            plt.ylabel("Return on day t + 1, %")
            fname = f"./scatter_plots/{ticker}_scatter_{time_delta}y.png"
            plt.savefig(fname = fname)
            # plt.show()
            plt.clf()
            