import pandas as pd
import yfinance as yf

from tradingbot.indicators.rsi import __getRSI__

data = pd.read_csv('datas/BTC1H2018-2024.csv')

rsi = __getRSI__(data, 14)

def simulate_trade(rsi, balance, trade_size):

    position = False

    for i in range(len(data)):
        if (position is False
            and rsi['RSI_Buy_Conf'].iloc[i]):

            position = False
            time = data['Close Time']
            price = data["Close"].iloc[i]
            quantity = trade_size / price

            print(f"Buy order: {time}, Price: {price}, Quantity: {quantity}")


balance = 10000
trade_size = balance * 0.1

simulate_trade(rsi, balance, trade_size)

print(rsi)



