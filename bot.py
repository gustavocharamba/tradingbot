import pandas as pd
import yfinance as yf

from trading.graph.graph import __getGraph__
from trading.indicators.macd import __getMACD__
from trading.indicators.stochastic import __getStochastic__
from trading.indicators.trix import __getTrix__
from trading.indicators.rsi import __getRSI__

# BTC Price History
btc_data = yf.Ticker("BTC-USD")
history = btc_data.history(period="6mo", interval="1h")  # 6 months of data

# Indicators Calculation
macd = __getMACD__(history)
stoch = __getStochastic__(history)
trix = __getTrix__(history)
rsi = __getRSI__(history)

# Function to simulate trading with balance control and trade size
def simulate_trading(history, macd, stoch, trix, rsi, initial_balance, trade_size):
    """
    Simulates trading based on MACD, Stochastic, TRIX, and RSI indicators.
    """
    position = None  # Either 'buy' or None (no active position)
    buy_price = 0  # Buy price
    sell_price = 0  # Sell price
    profits = []  # List to store profits/losses
    current_balance = initial_balance  # Starting balance
    btc_quantity = 0  # Quantity of BTC bought

    for i in range(1, len(history)):
        # Check buy conditions
        if (
            stoch['STOCH_Buy_Conf'].iloc[i]
            and macd['MACD_Buy_Conf'].iloc[i]
            and rsi['RSI_Buy_Conf'].iloc[i]
            and position is None
        ):
            trade_value = current_balance * trade_size
            btc_quantity = trade_value / history['Close'].iloc[i]
            position = 'buy'
            buy_price = history['Close'].iloc[i]
            current_balance -= trade_value

            # Print buy order details with RSI value
            rsi_value = rsi['RSI'].iloc[i]
            rsi_signal = rsi['RSI_Signal'].iloc[i]
            print(f"Buy order: {history.index[i]}, Price: {buy_price}, Quantity: {btc_quantity} BTC, RSI: {rsi_value}, RSI SMA: {rsi_signal}")

        # Check sell conditions
        elif position == 'buy' and (
            not macd['MACD_Buy_Conf'].iloc[i]
            or not stoch['STOCH_Buy_Conf'].iloc[i]
            or not trix['TRIX_Buy_Conf'].iloc[i]
            or rsi['RSI_Sell_Conf'].iloc[i]
        ):
            position = None
            sell_price = history['Close'].iloc[i]
            profit = (sell_price - buy_price) * btc_quantity
            current_balance += (btc_quantity * sell_price)
            profits.append(profit)
            print(f"Sell order: {history.index[i]}, Price: {sell_price}, Gain/Loss: {profit}")

    # Simulation summary
    total_profit = sum(profits)
    print(f"Total Gain: {total_profit}")
    print(f"Final Balance: {current_balance}")
    __getGraph__(history, macd, stoch, trix, rsi)  # Plot the graph
    return total_profit, current_balance

# Set initial balance and trade size
initial_balance = 10000  # Initial balance of $10,000
trade_size = 1  # Allocate 100% of the balance per trade

# Run the simulation
total_profit, final_balance = simulate_trading(history, macd, stoch, trix, rsi, initial_balance, trade_size)

# Display simulation results
print(f"Total Profit: {total_profit}")
print(f"Final Balance: {final_balance}")
