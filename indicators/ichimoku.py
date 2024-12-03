import pandas as pd

def __getIchimoku__(history, short_period=9, medium_period=26, long_period=52):
    """
    Calculates the Ichimoku Cloud components and identifies buy/sell confirmations.

    Parameters:
    - history (pd.DataFrame): Historical price data with columns: 'High', 'Low', and 'Close'.
    - short_period (int): Period for Tenkan-sen calculation. Default is 9.
    - medium_period (int): Period for Kijun-sen calculation. Default is 26.
    - long_period (int): Period for Senkou Span B calculation. Default is 52.

    Returns:
    - pd.DataFrame: DataFrame with Ichimoku components and buy/sell confirmations.
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

    # Define Buy Confirmation
    ichimoku_buy_conf = (
        (history['Close'] > senkou_span_a) &  # Price above Span A
        (history['Close'] > senkou_span_b) &  # Price above Span B
        (tenkan_sen > kijun_sen) &  # Tenkan-sen above Kijun-sen
        (history['Close'] > kijun_sen) &  # Price above Kijun-sen
        (chikou_span > history['Close'].shift(medium_period))  # Chikou Span above past price
    )

    # Define Sell Confirmation
    ichimoku_sell_conf = (
        (history['Close'] < senkou_span_a) &  # Price below Span A
        (history['Close'] < senkou_span_b) &  # Price below Span B
        (tenkan_sen < kijun_sen) &  # Tenkan-sen below Kijun-sen
        (history['Close'] < kijun_sen) &  # Price below Kijun-sen
        (chikou_span < history['Close'].shift(medium_period))  # Chikou Span below past price
    )

    return pd.DataFrame({
        'Tenkan_sen': tenkan_sen,
        'Kijun_sen': kijun_sen,
        'Senkou_Span_A': senkou_span_a,
        'Senkou_Span_B': senkou_span_b,
        'Chikou_Span': chikou_span,
        'Ichimoku_Buy_Conf': ichimoku_buy_conf,
        'Ichimoku_Sell_Conf': ichimoku_sell_conf
    })
