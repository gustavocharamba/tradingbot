import yfinance as yf
import time
import pandas as pd

from mavlog import __getMavLog__
from graph import __getGraph__
from didi import __getDidi__
from bollinger import __getBollinger__
from adx import __getAdx__
from trix import __getTrix__
from stochastic import __getStochastic__
# from botGraph import __getBotGraph__

#
btc_data = yf.Ticker("AAPL")
history = btc_data.history(period="1mo", interval="1h")
# history = pd.read_csv('BTCUSDT_H4.csv', index_col='Datetime', parse_dates=True)

didi = __getDidi__(history, 3, 21, 8)
boll = __getBollinger__(history, 8)
adx = __getAdx__(history, 8)
trix = __getTrix__(history, 4, 9)
stoch = __getStochastic__(history, 3, 14)
log_mav = __getMavLog__(history, 8)

def __getTrade__(balance, amount, period):
    aportes = []

    oper_buy = [False] * history.shape[0]
    oper_sell = [False] * history.shape[0]

    for i in range(history['Close'][-period:].shape[0]):

        if log_mav['mav9_buy_conf'].iloc[i] and balance >= amount:
            price = history['Close'].iloc[i]
            oper_buy[i] = True

            quantity = amount / price
            aportes.append([quantity, price])
            balance = balance - amount

            # __getBotGraph__(history, period, oper_buy, oper_sell)


        if log_mav['mav9_sell_conf'].iloc[i]:

            price = history['Close'].iloc[i]
            oper_sell[i] = True

            for j in aportes:
                lucro = j[0] * price - j[0] * j[1]
                print(lucro)
                balance = balance + j[0] * price

            # __getBotGraph__(history, period, oper_buy, oper_sell)

            aportes = []

    __getGraph__(history, -1, didi, boll, adx, trix, stoch, oper_buy, oper_sell)
    return balance, aportes, oper_buy, oper_sell

balance, aportes, oper_buy, oper_sell= __getTrade__(5000, 2500, -1)
print(f'BALANCE FINALIZADO: {balance}, APORTES FINALIZADOS: {aportes}')

