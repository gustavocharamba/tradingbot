import pandas as pd

def __getParabolicSAR__(history, step=0.02, max_step=0.2):
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
