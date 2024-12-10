import pandas as pd
import numpy as np
import yfinance as yf

def __getVWAP__(history):
    """
    Calculates the Volume Weighted Average Price (VWAP) and adds confirmation logic for buying.

    Parameters:
    - history (pd.DataFrame): Historical price data with 'High', 'Low', 'Close', and 'Volume' columns.

    Returns:
    - pd.DataFrame: DataFrame containing 'VWAP', 'VWAP_Buy_Conf', and other columns for plotting.
    """
    # Calculate Typical Price
    typical_price = (history['High'] + history['Low'] + history['Close']) / 3

    # Calculate cumulative TP*Volume and Volume
    cumulative_tp_volume = (typical_price * history['Volume']).cumsum()
    cumulative_volume = history['Volume'].cumsum()

    # Calculate VWAP
    vwap = cumulative_tp_volume / cumulative_volume

    # Define buy confirmation logic
    # Buy if the price is below VWAP and starting to rise
    vwap_buy_conf = (
        (history['Close'] < vwap) &  # Price is below VWAP
        (history['Close'] > history['Close'].shift(1))  # Price is rising
    )

    # Add results to DataFrame
    return pd.DataFrame({
        'VWAP': vwap,
        'VWAP_Buy_Conf': vwap_buy_conf,
        'Close': history['Close'],
        'High': history['High'],
        'Low': history['Low'],
        'Volume': history['Volume']
    })
