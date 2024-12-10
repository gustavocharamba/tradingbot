import os
import logging
import multiprocessing
import functools
import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.model_selection import ParameterGrid
from tqdm import tqdm

# Configurações de performance
os.environ['OPENBLAS_NUM_THREADS'] = '1'
np.seterr(all='ignore')

# Configuração de logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


# Funções de indicadores técnicos (placeholders - substitua pelas suas implementações originais)

def __getMACD__(history, fast_period, slow_period, signal_period):
    """
    Calculates the MACD with more frequent buy confirmation logic.

    Parameters:
    - history (pd.DataFrame): Historical price data with at least a 'Close' column.
    - fast_period (int): Fast period for MACD calculation. Default is 12.
    - slow_period (int): Slow period for MACD calculation. Default is 26.
    - signal_period (int): Signal line period for MACD. Default is 9.

    Returns:
    - pd.DataFrame: DataFrame containing 'MACD', 'Signal_Line', 'MACD_Histogram', 'MACD_Buy_Conf', and 'MACD_Sell_Conf'.
    """
    # Calculate MACD
    fast_ema = history['Close'].ewm(span=fast_period, adjust=False).mean()
    slow_ema = history['Close'].ewm(span=slow_period, adjust=False).mean()
    macd = fast_ema - slow_ema
    signal_line = macd.ewm(span=signal_period, adjust=False).mean()
    macd_histogram = macd - signal_line

    # Define more frequent buy confirmation (when MACD crosses above the signal line, regardless of MACD value)
    macd_buy_conf = (
        (macd > signal_line) &  # MACD crosses above the signal line
        (macd > macd.rolling(window=slow_period).mean())
    )

    return pd.DataFrame({
        'MACD': macd,
        'MACD_Signal': signal_line,
        'MACD_Histogram': macd_histogram,
        'MACD_Buy_Conf': macd_buy_conf,
    })

def __getRSI__(history, period):
    """
    Calculates the Relative Strength Index (RSI) with more frequent buy confirmation logic.

    Parameters:
    - history (pd.DataFrame): Historical price data with at least a 'Close' column.
    - period (int): Number of periods to use for RSI calculation. Default is 14.

    Returns:
    - pd.DataFrame: DataFrame containing 'RSI', 'RSI_Signal', 'RSI_Buy_Conf', and 'RSI_Sell_Conf'.
    """
    # Calculate price changes
    delta = history['Close'].diff()

    # Separate gains and losses
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    # Calculate exponential moving averages of gains and losses
    avg_gain = gain.ewm(com=(period - 1), min_periods=period).mean()
    avg_loss = loss.ewm(com=(period - 1), min_periods=period).mean()

    # Calculate Relative Strength (RS)
    rs = avg_gain / avg_loss

    # Calculate RSI
    rsi = 100 - (100 / (1 + rs))

    # Calculate short-term SMA of RSI (this will be used as RSI Signal)
    rsi_sma = rsi.rolling(window=3).mean()

    # Add RSI_Signal column to the DataFrame
    history['RSI_Signal'] = rsi_sma

    # Define more frequent buy confirmation (RSI above 30 and rising, no need for oversold condition)
    rsi_buy_conf = (
        (rsi > 30) &  # RSI above 30 (no oversold condition needed)
        (rsi > rsi.shift(1)) &  # RSI is rising
        (rsi > rsi_sma)  # RSI is above its short-term SMA
    )

    # Define sell confirmation conditions (same as before)
    rsi_sell_conf = (
        (rsi < 70) &  # RSI crosses below 70 (overbought threshold)
        (rsi.shift(1) >= 70)  # RSI was above or at 70 in the previous period
    )

    return pd.DataFrame({
        'RSI': rsi,
        'RSI_Signal': rsi_sma,
        'RSI_Buy_Conf': rsi_buy_conf,
        'RSI_Sell_Conf': rsi_sell_conf
    })

def __getIchimoku__(history, short_period, medium_period, long_period):
    """
    Calculates the Ichimoku Cloud components and identifies buy/sell confirmations.

    Parameters:
    - history (pd.DataFrame): Historical price data with columns: 'High', 'Low', and 'Close'.
    - short_period (int): Period for Tenkan-sen calculation. Default is 9.
    - medium_period (int): Period for Kijun-sen calculation. Default is 26.
    - long_period (int): Period for Senkou Span B calculation. Default is 52.

    Returns:
    - pd.DataFrame: DataFrame with Ichimoku components and buy/sell confirmation (True/False).
    """
    # Calculate Tenkan-sen (Conversion Line)
    tenkan_sen = (history['High'].rolling(window=short_period).max() +
                  history['Low'].rolling(window=short_period).min()) / 2

    # Calculate Kijun-sen (Base Line)
    kijun_sen = (history['High'].rolling(window=medium_period).max() +
                 history['Low'].rolling(window=medium_period).min()) / 2

    # Calculate Senkou Span A (Leading Span A)
    senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(medium_period)

    # Calculate Senkou Span B (Leading Span B)
    senkou_span_b = ((history['High'].rolling(window=long_period).max() +
                      history['Low'].rolling(window=long_period).min()) / 2).shift(medium_period)

    # Calculate Chikou Span (Lagging Span)
    chikou_span = history['Close'].shift(-medium_period)

    # Define Buy Confirmation (Ichimoku Buy Condition)
    ichimoku_buy_conf = (
        (history['Close'] > senkou_span_a) &  # Price above Span A
        (history['Close'] > senkou_span_b) &  # Price above Span B
        (tenkan_sen > kijun_sen) &  # Tenkan-sen above Kijun-sen
        (history['Close'] > kijun_sen) &  # Price above Kijun-sen
        (chikou_span > history['Close'].shift(medium_period))  # Chikou Span above past price
    )

    # Define Sell Confirmation (Ichimoku Sell Condition)
    ichimoku_sell_conf = (
        (history['Close'] < senkou_span_a) &  # Price below Span A
        (history['Close'] < senkou_span_b) &  # Price below Span B
        (tenkan_sen < kijun_sen) &  # Tenkan-sen below Kijun-sen
        (history['Close'] < kijun_sen) &  # Price below Kijun-sen
        (chikou_span < history['Close'].shift(medium_period))  # Chikou Span below past price
    )

    # Create a DataFrame with the indicator values, Buy Conf, and Sell Conf
    ichimoku_combined_values = pd.DataFrame({
        'Tenkan_sen': tenkan_sen,
        'Kijun_sen': kijun_sen,
        'Senkou_Span_A': senkou_span_a,
        'Senkou_Span_B': senkou_span_b,
        'Chikou_Span': chikou_span,
        'Ichimoku_Buy_Conf': ichimoku_buy_conf,
        'Ichimoku_Sell_Conf': ichimoku_sell_conf
    })

    # Return the DataFrame with Ichimoku values, Buy Conf, and Sell Conf
    return ichimoku_combined_values

def __getParabolicSAR__(history, step, max_step):
    """
    Calculates the Parabolic SAR (Stop and Reverse) and identifies buy/sell confirmations.

    Parameters:
    - history (pd.DataFrame): Historical price data with columns: 'High', 'Low', 'Close', and optionally 'Volume'.
    - step (float): Initial acceleration factor (AF). Default is 0.02.
    - max_step (float): Maximum acceleration factor (AF). Default is 0.2.

    Returns:
    - pd.DataFrame: DataFrame with Parabolic SAR values and buy/sell confirmations.
    """
    high = history['High']
    low = history['Low']
    close = history['Close']

    # Initialize variables
    sar = [low.iloc[0]]  # Starting with the first low as SAR
    ep = high.iloc[0]    # Extreme price starts with the first high
    af = step            # Acceleration factor starts with the step
    long_trend = True    # Start with an uptrend
    sar_values = []      # List to store SAR values
    trends = []          # List to track trend direction

    for i in range(1, len(history)):
        prev_sar = sar[-1]
        prev_ep = ep
        prev_af = af

        # Update SAR based on trend direction
        if long_trend:
            current_sar = prev_sar + prev_af * (prev_ep - prev_sar)
            current_sar = min(current_sar, low.iloc[i - 1], low.iloc[i])  # Limit SAR in uptrend
        else:
            current_sar = prev_sar + prev_af * (prev_ep - prev_sar)
            current_sar = max(current_sar, high.iloc[i - 1], high.iloc[i])  # Limit SAR in downtrend

        # Check for reversal
        if long_trend and close.iloc[i] < current_sar:
            long_trend = False
            current_sar = prev_ep  # Reversal sets SAR to previous extreme price
            ep = low.iloc[i]       # Reset extreme price
            af = step              # Reset AF
        elif not long_trend and close.iloc[i] > current_sar:
            long_trend = True
            current_sar = prev_ep  # Reversal sets SAR to previous extreme price
            ep = high.iloc[i]      # Reset extreme price
            af = step              # Reset AF
        else:
            # Update extreme price and AF if no reversal
            if long_trend:
                if high.iloc[i] > prev_ep:
                    ep = high.iloc[i]
                    af = min(prev_af + step, max_step)
            else:
                if low.iloc[i] < prev_ep:
                    ep = low.iloc[i]
                    af = min(prev_af + step, max_step)

        sar.append(current_sar)
        sar_values.append(current_sar)
        trends.append(long_trend)

    # Convert trends and SAR values to Pandas Series for alignment
    sar_series = pd.Series(sar_values, index=history.index[1:])
    trends = pd.Series(trends, index=history.index[1:])

    # Moving Average for robustness
    ma_period = 20
    ma = close.rolling(window=ma_period).mean()

    # Volume increase condition (optional if 'Volume' exists in data)
    if 'Volume' in history.columns:
        volume_increase = history['Volume'].pct_change() > 0.2  # 20% increase in volume
    else:
        volume_increase = pd.Series([False] * len(history), index=history.index)

    # RSI condition for overbought/oversold filtering
    rsi_period = 14
    delta = close.diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    # Define Buy Confirmation (More Robust)
    parabolic_sar_buy_conf = (
        trends &  # Current trend is bullish
        (close[1:] > sar_series) &  # Close price above SAR
        (close[1:] > ma[1:]) &  # Close price above Moving Average
        (~volume_increase.iloc[:-1].isna() & volume_increase.iloc[:-1]) &  # Volume increased
        (rsi[1:] < 70)  # RSI below overbought level
    )

    # Define Sell Confirmation
    parabolic_sar_sell_conf = (
        ~trends &  # Current trend is bearish
        (close[1:] < sar_series) &  # Close price below SAR
        (rsi[1:] > 30) &  # RSI above oversold level
        (rsi[1:] > rsi[1:].shift(1))
    )

    return pd.DataFrame({
        'Parabolic_SAR': sar_series,
        'ParabolicSAR_Buy_Conf': parabolic_sar_buy_conf,
        'ParabolicSAR_Sell_Conf': parabolic_sar_sell_conf
    }).reindex(history.index)  # Reindex to match the original DataFrame

def __getOBV__(history):
    """
    Calculates the On-Balance Volume (OBV) with more frequent buy/sell confirmation logic.

    Parameters:
    - history (pd.DataFrame): Historical price data with at least 'Close' and 'Volume' columns.

    Returns:
    - pd.DataFrame: DataFrame containing 'OBV', 'OBV_Buy_Conf', and 'OBV_Sell_Conf'.
    """
    # Calculate the daily price change
    price_change = history['Close'].diff()

    # Initialize the OBV series
    obv = [0]  # OBV starts at 0

    # Calculate OBV for each day
    for i in range(1, len(history)):
        if price_change.iloc[i] > 0:
            obv.append(obv[-1] + history['Volume'].iloc[i])  # If price goes up, add volume
        elif price_change.iloc[i] < 0:
            obv.append(obv[-1] - history['Volume'].iloc[i])  # If price goes down, subtract volume
        else:
            obv.append(obv[-1])  # If price is unchanged, OBV stays the same

    # Add OBV to the DataFrame
    history['OBV'] = obv

    # Define Buy confirmation: OBV is rising and price is also rising
    obv_buy_conf = (
        (history['OBV'] > history['OBV'].shift(1)) &  # OBV is rising
        (history['Close'] > history['Close'].shift(1))  # Price is also rising
    )

    # Define Sell confirmation: OBV is falling and price is also falling
    obv_sell_conf = (
        (history['OBV'] < history['OBV'].shift(1)) &  # OBV is falling
        (history['Close'] < history['Close'].shift(1))  # Price is also falling
    )

    # Add OBV Buy and Sell Confirms to the DataFrame
    history['OBV_Buy_Conf'] = obv_buy_conf
    history['OBV_Sell_Conf'] = obv_sell_conf

    # Return the DataFrame with OBV and Buy/Sell signals
    return pd.DataFrame({
        'OBV': history['OBV'],
        'OBV_Buy_Conf': history['OBV_Buy_Conf'],
        'OBV_Sell_Conf': history['OBV_Sell_Conf']
    })


@functools.lru_cache(maxsize=None)
def fetch_ticker_data(symbol, period="2y", interval="1h"):
    """Cachear dados de ticker com memoização"""
    try:
        ticker = yf.Ticker(symbol)
        return ticker.history(period=period, interval=interval)
    except Exception as e:
        logger.error(f"Erro ao buscar dados para {symbol}: {e}")
        return None


def backtest_strategy(symbols, ichimoku_params, rsi_params, macd_params, psar_params):
    """Simulação de estratégia de trading"""
    data = {}
    for symbol in symbols:
        history = fetch_ticker_data(symbol)

        if history is None or history.empty:
            logger.warning(f"Dados indisponíveis para {symbol}")
            continue

        # Calcular indicadores
        rsi = __getRSI__(history, period=rsi_params['rsi_period'])
        macd = __getMACD__(history, fast_period=macd_params['fast_period'],
                           slow_period=macd_params['slow_period'],
                           signal_period=macd_params['signal_period'])
        psar = __getParabolicSAR__(history, step=psar_params['step'],
                                   max_step=psar_params['max_step'])
        ichimoku = __getIchimoku__(history,
                                   short_period=ichimoku_params['short_period'],
                                   medium_period=ichimoku_params['medium_period'],
                                   long_period=ichimoku_params['long_period'])
        obv = __getOBV__(history)

        # Concatenar indicadores
        history = pd.concat([history, rsi, macd, psar, ichimoku, obv], axis=1)
        data[symbol] = history

    balances = {}
    for symbol, history in data.items():
        position = None
        balance = 10000

        for i in range(2, len(history)):
            # Condição de compra
            buy_condition = (
                    ichimoku["Ichimoku_Buy_Conf"].iloc[i]
                    and (obv["OBV_Buy_Conf"].iloc[i] or obv["OBV_Buy_Conf"].iloc[i - 1]
                         or obv["OBV_Buy_Conf"].iloc[i - 2] or obv["OBV_Buy_Conf"].iloc[i - 2])
                    and (psar['ParabolicSAR_Buy_Conf'].iloc[i] or psar['ParabolicSAR_Buy_Conf'].iloc[i - 1]
                         or psar['ParabolicSAR_Buy_Conf'].iloc[i - 2])
                    and rsi['RSI_Buy_Conf'].iloc[i]
                    and macd['MACD_Buy_Conf'].iloc[i]
                    and position is None
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


def process_single_param_set(params):
    """Processar um conjunto de parâmetros"""
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

    symbols = ["BTC-USD", "ETH-USD", "SOL-USD", "ADA-USD"]

    try:
        balances = backtest_strategy(symbols, ichimoku_params, rsi_params, macd_params, psar_params)
        total_balance = sum(balances.values())

        return {
            'params': params,
            'total_balance': total_balance,
            'balances': balances
        }
    except Exception as e:
        logger.error(f"Erro no processamento: {e}")
        return {
            'params': params,
            'total_balance': 10000 * len(symbols),  # Valor padrão em caso de erro
            'balances': {symbol: 10000 for symbol in symbols}
        }


def optimize_with_multiprocessing(grid):
    """Otimização paralela de parâmetros"""
    num_cores = multiprocessing.cpu_count()
    logger.info(f"Usando {num_cores} núcleos para processamento")

    with multiprocessing.Pool(processes=num_cores) as pool:
        results = list(tqdm(
            pool.imap(process_single_param_set, grid),
            total=len(grid),
            desc="Otimizando Parâmetros"
        ))

    # Encontrar melhor resultado
    best_result = max(results, key=lambda x: x['total_balance'])
    return best_result


def main():
    # Grid refinado de parâmetros
    param_grid = {
        'short_period': [5, 7 , 8 , 9],
        'medium_period': [24, 26],
        'long_period': [48, 50, 52],
        'rsi_period': [8, 10, 12, 14],
        'macd_fast_period': [8, 9, 11, 12],
        'macd_slow_period': [19, 21, 24, 25],
        'macd_signal_period': [7, 8, 9],
        'psar_step': [0.02, 0.025, 0.03],
        'psar_max_step': [0.2, 0.25, 0.3],
    }

    # Gerar grid de parâmetros
    grid = list(ParameterGrid(param_grid))

    # Executar otimização
    best_result = optimize_with_multiprocessing(grid)

    # Imprimir resultados
    logger.info(f"Melhores Parâmetros: {best_result['params']}")
    logger.info(f"Resultado Total: {best_result['total_balance']}")
    logger.info("Detalhes dos Balanços:")
    for symbol, balance in best_result['balances'].items():
        logger.info(f"{symbol}: {balance}")


if __name__ == "__main__":
    main()