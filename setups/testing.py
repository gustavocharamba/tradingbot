import yfinance as yf
from tradingbot.indicators.macd import __getMACD__
from tradingbot.indicators.eden import __getEdenSetup__

btc_data = yf.Ticker("BTC-USD")
history = btc_data.history(period="3mo", interval="1h")
macd = __getMACD__(history, 144, 244, 12)

def __getTrade__():
    best_balance = 0
    best_i = 0
    best_j = 0

    for i in range(5, 21):
        for j in range(60, 100):
            balance = 5000
            initial_balance = balance

            for idx in range(history['Close'].shape[0]):
                eden = __getEdenSetup__(history, i, j)
                position_open = False
                operation = 0
                quantity = 0

                if eden['eden_buy_conf'].iloc[idx] and macd['macd_buy_conf'].iloc[idx] and not position_open:
                    price = history['Close'].iloc[idx]
                    quantity = balance / price
                    operation = quantity * price
                    position_open = True

                if position_open:
                    # Close position if profit is 3% or loss is 1%
                    if (history['Close'].iloc[idx] >= (operation * 1.03)) or (history['Close'].iloc[idx] <= (operation * 0.99)):
                        price = history['Close'].iloc[idx]
                        balance = balance * (1 + (price - operation) / operation)
                        position_open = False

            # Calculate gain or loss based on initial balance
            gain_or_loss = ((balance - initial_balance) / initial_balance) * 100
            print(f"i={i}, j={j}, Gain or Loss (%): {gain_or_loss}, Balance: {balance}")

            if balance > best_balance:
                best_balance = balance
                best_i = i
                best_j = j

    return best_balance, best_i, best_j

best_balance, best_i, best_j = __getTrade__()

print(f'BALANCE FINALIZED: {best_balance}')
print(f'Best Parameters: i={best_i}, j={best_j}')
