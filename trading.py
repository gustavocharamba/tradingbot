import yfinance as yf
import time

from graph import __getGraph__
from didi import __getDidi__
from bollinger import __getBollinger__
from adx import __getAdx__
from trix import __getTrix__
from stochastic import __getStochastic__
from botGraph import __getBotGraph__

while True:
    btc_data = yf.Ticker("BTC-USD")
    history = btc_data.history(period="1d", interval="5m")

    didi = __getDidi__(history, 5, 21, 9)
    boll = __getBollinger__(history, 8)
    adx = __getAdx__(history, 8)
    trix = __getTrix__(history, 4, 9)
    stoch = __getStochastic__(history, 3, 14)

    def __getTrade__(balance, amount, period):
        aportes = []

        oper_buy = [False] * history.shape[0]
        oper_sell = [False] * history.shape[0]

        i = history['Close'].shape[0]

        for i in range(i, history['Close'].shape[0]):

            if didi['didi_buy_alert'].iloc[i] and balance >= amount:
                price = history['Close'].iloc[i]
                oper_buy[i] = True

                quantity = amount / price
                aportes.append([quantity, price])
                balance = balance - amount

                __getBotGraph__(history, period, oper_buy, oper_sell)


            # if didi['didi_sell_alert'].iloc[i] == True:
            #
            #     price = history['Close'].iloc[i]
            #     oper_sell[i] = True
            #
            #     for j in aportes:
            #         lucro = j[0] * price - j[0] * j[1]
            #         print(lucro)
            #         balance = balance + j[0] * price

                __getBotGraph__(history, period, oper_buy, oper_sell)

                aportes = []

        return balance, aportes, oper_buy, oper_sell

    __getTrade__(5000, 2500, 15)
