import yfinance as yf

from graps.edenGraph import __getEdenGraph__
from indicators.macd import __getMACD__
from tradingbot.indicators.eden import __getEdenSetup__

btc_data = yf.Ticker("BTC-USD")
history = btc_data.history(period="1mo", interval="5m")

macd = __getMACD__(history, 10000,144, 244, 12)
eden = __getEdenSetup__(history, 10000, 8, 80)
def __getTrade__(balance, amount, period):
    aportes = []

    oper_buy = [False] * history.shape[0]
    oper_sell = [False] * history.shape[0]

    oper_buy_price = 0

    position_open = False

    for i in range(history['Close'][-period:].shape[0]):
        if eden['eden_buy_conf'].iloc[i] and macd['macd_buy_conf'].iloc[i] and balance >= amount and not position_open:
            price = history['Close'].iloc[i]
            oper_buy_price = price
            oper_buy[i] = True
            position_open = True  # Marca que uma posição está aberta

            quantity = amount / price
            aportes.append([quantity, price])
            balance = balance - amount

        # Verifica se uma posição está aberta antes de tentar vender
        if position_open:
            if (history['Close'].iloc[i] > (oper_buy_price * 1.03) or history['Close'].iloc[i] < (
                    oper_buy_price * 0.985)) and oper_buy_price != 0:
                price = history['Close'].iloc[i]
                oper_sell[i] = True
                position_open = False  # Marca que a posição está fechada

                for j in aportes:
                    lucro = j[0] * price - j[0] * j[1]
                    print(lucro)
                    balance = balance + j[0] * price

                oper_buy_price = 0
                aportes = []

    __getEdenGraph__(history, -1, eden, macd, oper_buy, oper_sell)
    return balance, aportes, oper_buy, oper_sell

balance, aportes, oper_buy, oper_sell= __getTrade__(50000, 5000, -1)
print(f'BALANCE FINALIZADO: {balance}, APORTES FINALIZADOS: {aportes}')
