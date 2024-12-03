import pandas as pd

def __getMACD__(history, fast_period=12, slow_period=26, signal_period=9):
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
        (macd > signal_line) & (macd > -500) # MACD crosses above the signal line
    )

    return pd.DataFrame({
        'MACD': macd,
        'Signal_Line': signal_line,
        'MACD_Histogram': macd_histogram,
        'MACD_Buy_Conf': macd_buy_conf,
    })
