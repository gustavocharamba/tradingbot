import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Baixar dados históricos de preços do Bitcoin
data = yf.download('BTC-USD', start='2020-01-01', end='2024-04-01', interval='1d')
data['EMA9'] = data['Close'].ewm(span=9, adjust=False).mean()
data['EMA11'] = data['Close'].ewm(span=11, adjust=False).mean()

# Identificar cruzamentos
data['Position'] = None
data.loc[(data['EMA9'] > data['EMA11']) & (data['EMA9'].shift() < data['EMA11'].shift()), 'Position'] = 'buy'
data.loc[(data['EMA9'] < data['EMA11']) & (data['EMA9'].shift() > data['EMA11'].shift()), 'Position'] = 'sell'

# Estratégia de alavancagem
initial_balance = 10000
balance = initial_balance
quantity = 0
trades = []
balance_history = []

for index, row in data.iterrows():
    if row['Position'] == 'buy' and balance > 0:
        quantity = balance / row['Close']
        entry_price = row['Close']
        trades.append({'type': 'buy', 'price': entry_price, 'quantity': quantity})
        balance_history.append({'timestamp': index, 'balance': balance})
    elif quantity > 0:
        # Para posições LONG
        if row['Position'] == 'sell' or (row['Close'] >= entry_price * 1.05) or (row['Close'] <= entry_price * 0.97):
            exit_price = row['Close']
            balance = quantity * exit_price
            trades.append({'type': 'sell', 'price': exit_price, 'quantity': quantity, 'profit': balance - initial_balance})
            quantity = 0  # Fecha a posição
            balance_history.append({'timestamp': index, 'balance': balance})

# Resultado final
print(f"Final balance: {balance}")
print("Trade history:")
for trade in trades:
    print(trade)

# Plotando os resultados
fig = go.Figure(data=[go.Candlestick(x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'])])

# Marcando operações de compra e venda
buys = data[data['Position'] == 'buy']
sells = data[data['Position'] == 'sell']
fig.add_trace(go.Scatter(x=buys.index, y=buys['Close'], mode='markers', marker=dict(color='green', size=10), name='Buy'))
fig.add_trace(go.Scatter(x=sells.index, y=sells['Close'], mode='markers', marker=dict(color='red', size=10), name='Sell'))

# Adicionando o histórico de saldo
balance_df = pd.DataFrame(balance_history)
fig.add_trace(go.Scatter(x=balance_df['timestamp'], y=balance_df['balance'], mode='lines', name='Balance'))

fig.show()