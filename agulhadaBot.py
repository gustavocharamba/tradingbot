import yfinance as yf

from tradingbot.indicators.ema import __getEMA__
from tradingbot.graps.didiGraph import __getGraph__
from tradingbot.indicators.didi import __getDidi__
from tradingbot.indicators.bollinger import __getBollinger__
from tradingbot.indicators.adx import __getAdx__
from tradingbot.indicators.trix import __getTrix__
from tradingbot.indicators.stochastic import __getStochastic__
# from botGraph import __getBotGraph__
from tradingbot.setups.trendline import __trendline__
#
btc_data = yf.Ticker("BTC-USD")
history = btc_data.history(period="1mo", interval="1h")
# history = pd.read_csv('BTCUSDT_H4.csv', index_col='Datetime', parse_dates=True)

didi = __getDidi__(history, 3, 21, 8)
boll = __getBollinger__(history, 8)
adx = __getAdx__(history, 8)
trix = __getTrix__(history, 4, 9)
stoch = __getStochastic__(history, 3, 14)
ema = __getEMA__(history, 8, 20)
trendline = __trendline__(history)
def __getTrade__(balance, amount, period):
    aportes = []

    oper_buy = [False] * history.shape[0]
    oper_sell = [False] * history.shape[0]

    for i in range(history['Close'][-period:].shape[0]):

        if ema['ema_buy_conf'].iloc[i]:
            price = history['Close'].iloc[i]
            oper_buy[i] = True

            quantity = amount / price
            aportes.append([quantity, price])
            balance = balance - amount

            # __getBotGraph__(history, period, oper_buy, oper_sell)


        if ema['ema_sell_conf'].iloc[i]:

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

balance, aportes, oper_buy, oper_sell= __getTrade__(10000, 10000, -1)
print(f'BALANCE FINALIZADO: {balance}, APORTES FINALIZADOS: {aportes}')

