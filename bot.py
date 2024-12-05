import pandas as pd
import yfinance as yf

from tradingbot.graph.graph import __getGraph__
from tradingbot.indicators.macd import __getMACD__
from tradingbot.indicators.rsi import __getRSI__
from tradingbot.indicators.ichimoku import __getIchimoku__
from tradingbot.indicators.obv import __getOBV__
from tradingbot.indicators.PSAR import __getParabolicSAR__

symbol = "MSFT"

btc_data = yf.Ticker(symbol)
history = btc_data.history(period="2y", interval="1h")  # 2 years of data

# Indicators Calculation
macd = __getMACD__(history)
rsi = __getRSI__(history)
ichimoku = __getIchimoku__(history)
obv = __getOBV__(history)
psar = __getParabolicSAR__(history)

# Function to simulate trading with balance control, trade size, and monthly additions
def simulate_trading(history, macd, rsi, ichimoku, obv, psar, initial_balance, trade_size, monthly_addition):
    """
    Simulates trading based on MACD, RSI, Ichimoku, OBV, and Bollinger Bands indicators.
    Adds a fixed amount to the balance every month.
    """
    position = None  # Either 'buy' or None (no active position)
    buy_price = 0  # Buy price
    sell_price = 0  # Sell price
    profits = []  # List to store profits/losses
    current_balance = initial_balance  # Starting balance
    btc_quantity = 0  # Quantity of BTC bought

    # Track the last month for monthly additions
    last_month = history.index[0].month

    # Lists to store executed buy/sell signals
    executed_buy_signals = []
    executed_sell_signals = []

    # Simulation loop
    for i in range(1, len(history)):
        # Check if a new month has started and add the monthly addition
        current_month = history.index[i].month
        if current_month != last_month:
            current_balance += monthly_addition
            print(f"Monthly addition: {monthly_addition} added on {history.index[i]}. New Balance: {current_balance}")
            last_month = current_month

        if (
                ichimoku["Ichimoku_Buy_Conf"].iloc[i]
                and (obv["OBV_Buy_Conf"].iloc[i] or obv["OBV_Buy_Conf"].iloc[i - 1] or obv["OBV_Buy_Conf"].iloc[i - 2] or obv["OBV_Buy_Conf"].iloc[i - 2])
                and (psar['ParabolicSAR_Buy_Conf'].iloc[i] or psar['ParabolicSAR_Buy_Conf'].iloc[i - 1] or psar['ParabolicSAR_Buy_Conf'].iloc[i - 2])
                and rsi['RSI_Buy_Conf'].iloc[i]
                and macd['MACD_Buy_Conf'].iloc[i]
                and position is None
        ):
            # Buy conditions met, open a position
            trade_value = current_balance * trade_size
            btc_quantity = trade_value / history['Close'].iloc[i]
            position = 'buy'
            buy_price = history['Close'].iloc[i]
            current_balance -= trade_value
            executed_buy_signals.append(history.iloc[i])  # Store the buy signal
            print(f"Buy order: {history.index[i]}, Price: {buy_price}, Quantity: {btc_quantity} {symbol}")

        elif position == 'buy':
            # Sell conditions: Ichimoku Sell, Stop loss, or Take profit
            sell_condition = (
                    ichimoku["Ichimoku_Sell_Conf"].iloc[i]
            )
            if sell_condition:
                position = None
                sell_price = history['Close'].iloc[i]
                profit = (sell_price - buy_price) * btc_quantity
                current_balance += btc_quantity * sell_price
                profits.append(profit)
                executed_sell_signals.append(history.iloc[i])  # Store the sell signal
                print(f"Sell order: {history.index[i]}, Price: {sell_price}, Gain/Loss: {profit}")

    # Simulation summary
    total_profit = sum(profits)
    total_trades = len(profits)
    winning_trades = sum(1 for profit in profits if profit > 0)
    losing_trades = total_trades - winning_trades
    win_percentage = (winning_trades / total_trades * 100) if total_trades > 0 else 0

    # Display the results inside the function to avoid repetition
    print(f"Total Gain: {total_profit}")
    print(f"Final Balance: {current_balance}")
    print(f"Total Trades: {total_trades}")
    print(f"Winning Trades: {winning_trades}")
    print(f"Losing Trades: {losing_trades}")
    print(f"Win Percentage: {win_percentage:.2f}%")

    # Convert the executed signals to DataFrames before passing them to the graph function
    executed_buy_signals_df = pd.DataFrame(executed_buy_signals)
    executed_sell_signals_df = pd.DataFrame(executed_sell_signals)

    # Plot the graph with executed buy and sell signals
    __getGraph__(history, macd, rsi, ichimoku, executed_buy_signals_df, executed_sell_signals_df)

    return total_profit, current_balance, win_percentage

# Set initial balance, trade size, and monthly addition
initial_balance = 10000  # Initial balance of $10,000
trade_size = 1  # Allocate 100% of the balance per trade
monthly_addition = 500  # Add $1,000 to the balance every month

# Run the simulation
total_profit, final_balance, win_percentage = simulate_trading(history, macd, rsi, ichimoku, obv, psar, initial_balance, trade_size, monthly_addition)
