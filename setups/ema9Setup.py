import yfinance as yf
import pandas as pd
import plotly.graph_objs as go

from tradingbot.indicators.ema import __getEMA__

btc_data = yf.Ticker("BTC-USD")  # Assuming Bitcoin data
history = btc_data.history(period="3mo", interval="1h")

ema = __getEMA__(history, 10000, 9, 11)

def get_trades(balance, amount, period):
    trades = []
    total_balance = balance

    oper_buy = [False] * history.shape[0]
    oper_sell = [False] * history.shape[0]

    oper_buy_price = 0
    oper_sell_price = 0

    position_open = False
    is_long = False

    for i in range(history['Close'][-period:].shape[0]):
        trade_profit_loss = 0

        if ema['ema_buy_conf'].iloc[i] and balance >= amount and not position_open:
            price = history['Close'].iloc[i]
            oper_buy_price = price
            oper_buy[i] = True
            position_open = True
            is_long = True
            quantity = amount / price
            balance = balance - amount
            trades.append([price, 'Buy'])
        elif position_open:
            if is_long and ema['ema_sell_conf'].iloc[i] and oper_buy_price != 0:
                price = history['Close'].iloc[i]
                oper_sell[i] = True
                position_open = False
                trade_profit_loss = price - oper_buy_price
                balance = balance + amount + (amount * trade_profit_loss / oper_buy_price)
                trades[-1].append(price)
                trades[-1].append(trade_profit_loss)
            elif not is_long and ema['ema_buy_conf'].iloc[i] and oper_sell_price != 0:
                price = history['Close'].iloc[i]
                oper_buy[i] = True
                position_open = False
                trade_profit_loss = oper_sell_price - price
                balance = balance + amount + (amount * trade_profit_loss / oper_sell_price)
                trades[-1].append(price)
                trades[-1].append(trade_profit_loss)
        elif not position_open and (ema['ema_sell_conf'].iloc[i] or ema['ema_buy_conf'].iloc[i]):
            if is_long:
                oper_sell_price = history['Close'].iloc[i]
                is_long = False
            else:
                oper_buy_price = history['Close'].iloc[i]
                is_long = True

    return balance, trades

final_balance, trades = get_trades(5000, 2500, 10000)

print("Final Balance:", final_balance)
print("Trades:")
for idx, trade in enumerate(trades):
    print(f"Trade {idx + 1}: Entry Price: {trade[0]}, Exit Price: {trade[1]}, Profit/Loss: {trade[2]}")
