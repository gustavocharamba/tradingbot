import pandas as pd
import yfinance as yf
from sklearn.model_selection import ParameterGrid


def __getIchimoku__(history, short_period=8, medium_period=24, long_period=50):
    # Cálculos do Ichimoku conforme já feito
    tenkan_sen = (history['High'].rolling(window=short_period).max() +
                  history['Low'].rolling(window=short_period).min()) / 2
    kijun_sen = (history['High'].rolling(window=medium_period).max() +
                 history['Low'].rolling(window=medium_period).min()) / 2
    senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(medium_period)
    senkou_span_b = ((history['High'].rolling(window=long_period).max() +
                      history['Low'].rolling(window=long_period).min()) / 2).shift(medium_period)
    chikou_span = history['Close'].shift(-medium_period)

    ichimoku_buy_conf = (
            (history['Close'] > senkou_span_a) &
            (history['Close'] > senkou_span_b) &
            (tenkan_sen > kijun_sen) &
            (history['Close'] > kijun_sen) &
            (chikou_span > history['Close'].shift(medium_period))
    )
    ichimoku_sell_conf = (
            (history['Close'] < senkou_span_a) &
            (history['Close'] < senkou_span_b) &
            (tenkan_sen < kijun_sen) &
            (history['Close'] < kijun_sen) &
            (chikou_span < history['Close'].shift(medium_period))
    )

    ichimoku_combined_values = pd.DataFrame({
        'Tenkan_sen': tenkan_sen,
        'Kijun_sen': kijun_sen,
        'Senkou_Span_A': senkou_span_a,
        'Senkou_Span_B': senkou_span_b,
        'Chikou_Span': chikou_span,
        'Ichimoku_Buy_Conf': ichimoku_buy_conf,
        'Ichimoku_Sell_Conf': ichimoku_sell_conf
    })

    return ichimoku_combined_values


def __getOBV__(history):
    price_change = history['Close'].diff()
    obv = [0]
    for i in range(1, len(history)):
        if price_change.iloc[i] > 0:
            obv.append(obv[-1] + history['Volume'].iloc[i])
        elif price_change.iloc[i] < 0:
            obv.append(obv[-1] - history['Volume'].iloc[i])
        else:
            obv.append(obv[-1])
    history['OBV'] = obv

    obv_buy_conf = (
            (history['OBV'] > history['OBV'].shift(1)) &
            (history['Close'] > history['Close'].shift(1))
    )
    obv_sell_conf = (
            (history['OBV'] < history['OBV'].shift(1)) &
            (history['Close'] < history['Close'].shift(1))
    )

    history['OBV_Buy_Conf'] = obv_buy_conf
    history['OBV_Sell_Conf'] = obv_sell_conf

    return history


def __getRSI__(history, period=14):
    delta = history['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    rsi_buy_conf = rsi < 30  # Buy when RSI is below 30 (oversold)
    rsi_sell_conf = rsi > 70  # Sell when RSI is above 70 (overbought)

    history['RSI'] = rsi
    history['RSI_Buy_Conf'] = rsi_buy_conf
    history['RSI_Sell_Conf'] = rsi_sell_conf

    return history


def backtest_strategy(symbols, ichimoku_params, rsi_params, obv_params):
    # Download historical data for multiple symbols
    data = {}
    for symbol in symbols:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period="2y", interval="1h")
        history = __getRSI__(history, period=rsi_params['rsi_period'])
        history = __getOBV__(history)
        ichimoku = __getIchimoku__(history, short_period=ichimoku_params['short_period'],
                                   medium_period=ichimoku_params['medium_period'],
                                   long_period=ichimoku_params['long_period'])
        history = pd.concat([history, ichimoku], axis=1)
        data[symbol] = history

    # Backtest logic (simples para exemplo)
    balances = {}
    for symbol, history in data.items():
        position = None
        balance = 10000  # Starting balance for each symbol
        for i in range(2, len(history)):
            buy_condition = (
                    ichimoku["Ichimoku_Buy_Conf"].iloc[i] and
                    (history["OBV_Buy_Conf"].iloc[i] or
                     history["OBV_Buy_Conf"].iloc[i - 1] or
                     history["OBV_Buy_Conf"].iloc[i - 2]) and
                    history['RSI_Buy_Conf'].iloc[i]
            )

            if buy_condition and position is None:
                position = 'buy'
                buy_price = history['Close'].iloc[i]

            elif position == 'buy':
                sell_condition = ichimoku["Ichimoku_Sell_Conf"].iloc[i]
                if sell_condition:
                    sell_price = history['Close'].iloc[i]
                    profit = sell_price - buy_price
                    balance += profit
                    position = None

        balances[symbol] = balance

    return balances


# Definir intervalos para otimização
param_grid = {
    'short_period': [8, 9, 10],
    'medium_period': [24, 26, 28],
    'long_period': [50, 52, 54],
    'rsi_period': [10, 14, 20],
    'obv_period': [10, 14, 20]
}

# Gerar todas as combinações possíveis de parâmetros
grid = ParameterGrid(param_grid)

best_balance = 0
best_params = None
best_ichimoku_params = None
best_rsi_params = None
best_obv_params = None

for params in grid:
    ichimoku_params = {k: params[k] for k in ['short_period', 'medium_period', 'long_period']}
    rsi_params = {'rsi_period': params['rsi_period']}
    obv_params = {'obv_period': params['obv_period']}

    balances = backtest_strategy(["BTC-USD", "ETH-USD", "SOL-USD", "ADA-USD"], ichimoku_params, rsi_params, obv_params)

    total_balance = sum(balances.values())
    if total_balance > best_balance:
        best_balance = total_balance
        best_params = params
        best_ichimoku_params = ichimoku_params
        best_rsi_params = rsi_params
        best_obv_params = obv_params

# Exibir apenas os melhores parâmetros e o saldo final
print(f"Melhor parâmetro para Ichimoku: {best_ichimoku_params}")
print(f"Melhor parâmetro para RSI: {best_rsi_params}")
print(f"Melhor parâmetro para OBV: {best_obv_params}")
print(f"Melhor resultado (balance total): {best_balance}")
