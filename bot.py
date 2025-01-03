import pandas as pd
import yfinance as yf

from tradingbot.indicators.rsi import __getRSI__

data = pd.read_csv('datas/BTC1H2018-2024.csv')

rsi = __getRSI__(data, 9)

print(rsi)



