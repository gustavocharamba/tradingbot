import pandas as pd

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