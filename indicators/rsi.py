import pandas as pd

def __getRSI__(history, period=14):
    """
    Calculates the Relative Strength Index (RSI) with robust buy confirmation logic.

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

    # Calculate short-term SMA of RSI
    rsi_sma = rsi.rolling(window=3).mean()

    # Define robust buy confirmation conditions
    rsi_buy_conf = (
        (rsi > 30) &  # RSI crosses above 30 (oversold threshold)
        (rsi.shift(1) <= 30) &  # RSI was below or at 30 in the previous period
        (rsi > rsi.shift(1)) &  # RSI is rising
        (rsi > rsi_sma)  # RSI is above its short-term SMA
    )

    # Define sell confirmation conditions
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
