from sklearn.model_selection import ParameterGrid
import pandas as pd
import yfinance as yf
from tqdm import tqdm

from tradingbot.indicators.macd import __getMACD__
from tradingbot.indicators.rsi import __getRSI__
from tradingbot.indicators.ichimoku import __getIchimoku__
from tradingbot.indicators.PSAR import __getParabolicSAR__
from tradingbot.indicators.obv import __getOBV__

def backtest_strategy(symbols, ichimoku_params, rsi_params, macd_params, psar_params):
    data = {}
    for symbol in symbols:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period="2y", interval="1h")

        rsi = __getRSI__(history, period=rsi_params['rsi_period'])
        macd = __getMACD__(history, fast_period=macd_params['fast_period'], slow_period=macd_params['slow_period'],
                           signal_period=macd_params['signal_period'])
        psar = __getParabolicSAR__(history, step=psar_params['step'], max_step=psar_params['max_step'])
        ichimoku = __getIchimoku__(history, short_period=ichimoku_params['short_period'],
                                   medium_period=ichimoku_params['medium_period'],
                                   long_period=ichimoku_params['long_period'])
        obv = __getOBV__(history)

        history = pd.concat([history, rsi, macd, psar, ichimoku, obv], axis=1)
        data[symbol] = history

    balances = {}
    for symbol, history in data.items():
        position = None
        balance = 10000
        for i in range(2, len(history)):
            buy_condition = (
                history["Ichimoku_Buy_Conf"].iloc[i]
                and history['RSI_Buy_Conf'].iloc[i]
                and history['MACD_Buy_Conf'].iloc[i]
                and (psar['ParabolicSAR_Buy_Conf'].iloc[i] or psar['ParabolicSAR_Buy_Conf'].iloc[i - 1] or
                     psar['ParabolicSAR_Buy_Conf'].iloc[i - 2])

            )

            if buy_condition and position is None:
                position = 'buy'
                buy_price = history['Close'].iloc[i]

            elif position == 'buy':
                sell_condition = history["Ichimoku_Sell_Conf"].iloc[i]
                if sell_condition:
                    sell_price = history['Close'].iloc[i]
                    balance += sell_price - buy_price
                    position = None

        balances[symbol] = balance

    return balances


param_grid = {
    'short_period': range(1, 5),
    'medium_period': range(5, 10),
    'long_period': range(10, 15),
    'rsi_period': range(5, 15),
    'macd_fast_period': range(5, 10),
    'macd_slow_period': range(10, 15),
    'macd_signal_period': range(5, 8),
    'psar_step': [0.02, 0.03],
    'psar_max_step': [0.2, 0.3],
}

grid = ParameterGrid(param_grid)

best_balance = 0
best_params = None

for params in tqdm(grid, desc="Otimização de parâmetros"):
    ichimoku_params = {k: params[k] for k in ['short_period', 'medium_period', 'long_period']}
    rsi_params = {'rsi_period': params['rsi_period']}
    macd_params = {
        'fast_period': params['macd_fast_period'],
        'slow_period': params['macd_slow_period'],
        'signal_period': params['macd_signal_period'],
    }
    psar_params = {
        'step': params['psar_step'],
        'max_step': params['psar_max_step'],
    }

    balances = backtest_strategy(["BTC-USD", "ETH-USD", "SOL-USD", "ADA-USD"], ichimoku_params, rsi_params, macd_params,
                                 psar_params)
    total_balance = sum(balances.values())

    if total_balance > best_balance:
        best_balance = total_balance
        best_params = params

print(f"Melhores parâmetros: {best_params}")
print(f"Melhor resultado (balance total): {best_balance}")
