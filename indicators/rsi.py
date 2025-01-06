import pandas as pd


def __getRSI__(history, period):

    # Calculate price changes
    delta = history['Close'].diff()

    # Separate gains and losses
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    # Calculate exponential moving averages of gains and losses
    avg_gain = gain.ewm(span=period, min_periods=period).mean()
    avg_loss = loss.ewm(span=period, min_periods=period).mean()

    # Calculate Relative Strength (RS)
    rs = avg_gain / avg_loss

    # Calculate RSI
    rsi = 100 - (100 / (1 + rs))

    # Calculate short-term SMA of RSI (RSI Signal)
    rsi_signal = rsi.rolling(window=3).mean()

    rsi_buy_conf = rsi <= 60

    return pd.DataFrame({
        'RSI': rsi,
        'RSI_Signal': rsi_signal,
        'RSI_Buy_Conf': rsi_buy_conf
    })
