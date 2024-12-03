import pandas as pd

def __getBollingerBands__(history, window=20, num_std_dev=2):
    """
    Calculates the Bollinger Bands and generates buy/sell signals based on them.

    Parameters:
    - history (pd.DataFrame): Historical price data with at least a 'Close' column.
    - window (int): Number of periods for the moving average (default is 20).
    - num_std_dev (int): Number of standard deviations for the bands (default is 2).

    Returns:
    - pd.DataFrame: DataFrame containing 'Middle_Band', 'Upper_Band', 'Lower_Band', 'Buy_Conf', and 'Sell_Conf'.
    """
    # Calculate the moving average (SMA) and rolling standard deviation
    middle_band = history['Close'].rolling(window=window).mean()
    rolling_std = history['Close'].rolling(window=window).std()

    # Calculate the upper and lower bands
    upper_band = middle_band + (rolling_std * num_std_dev)
    lower_band = middle_band - (rolling_std * num_std_dev)

    # Define buy and sell conditions
    # Buy when price crosses below the lower band
    buy_conf = (history['Close'] < lower_band)
    # Sell when price crosses above the upper band
    sell_conf = (history['Close'] > upper_band)

    return pd.DataFrame({
        'Middle_Band': middle_band,
        'Upper_Band': upper_band,
        'Lower_Band': lower_band,
        'Bollinger_Buy_Conf': buy_conf,
        'Bollinger_Sell_Conf': sell_conf
    })
