import yfinance as yf

# Substitua estas funções com as versões corretas das suas funções personalizadas.
from tradingbot.indicators.macd import __getMACD__
from tradingbot.indicators.eden import __getEdenSetup__

btc_data = yf.Ticker("BTC-USD")
history = btc_data.history(period="3mo", interval="1h")
macd = __getMACD__(history, 144, 244, 12)


def getTrade():
    best_balance = 0
    best_i = 0
    best_j = 0

    for i in range(5, 21):
        for j in range(60, 100):
            balance = 5000
            position_open = False
            quantity = 0
            operation = 0

            for idx in range(history['Close'].shape[0]):
                eden = __getEdenSetup__(history, i, j)

                if eden['eden_buy_conf'].iloc[idx] and macd['macd_buy_conf'].iloc[idx] and not position_open:
                    price = history['Close'].iloc[idx]
                    quantity = balance / price
                    operation = quantity * price
                    position_open = True

                if position_open and ((history['Close'].iloc[idx] >= (operation * 1.03)) or (
                        history['Close'].iloc[idx] <= (operation * 0.99))):
                    price = history['Close'].iloc[idx]
                    balance = balance + (price * quantity) - operation
                    position_open = False

            if balance > best_balance:
                best_balance = balance
                best_i = i
                best_j = j

    return best_balance, best_i, best_j


best_balance, best_i, best_j = getTrade()

print(f'BALANCE FINALIZED: {best_balance}')
print(f'Best  Parameters: i={best_i}, j={best_j}')