import pandas as pd
import numpy as np


def __getAdx__(history, ref):
    high_low = history['High'] - history['Low']

    high_prev_close = np.abs(history['High'] - history['Close'].shift(1))
    low_prev_close = np.abs(history['Low'] - history['Close'].shift(1))

    tr = np.maximum.reduce([high_low, high_prev_close, low_prev_close])

    dm_high = np.where((history['High'] - history['High'].shift(1)) > (history['Low'].shift(1) - history['Low']),
                       history['High'] - history['High'].shift(1),
                       0)

    dm_high = np.where(dm_high > 0, dm_high, 0)

    dm_low = np.where((history['Low'].shift(1) - history['Low']) > (history['High'] - history['High'].shift(1)),
                      history['Low'].shift(1) - history['Low'], 0)

    dm_low = np.where(dm_low > 0, dm_low, 0)

    tr_series = pd.Series(tr, index=history.index)
    dm_high_series = pd.Series(dm_high, index=history.index)
    dm_low_series = pd.Series(dm_low, index=history.index)

    tr14 = tr_series.rolling(ref, min_periods=1).sum()
    dm_high_14 = dm_high_series.rolling(ref, min_periods=1).sum()
    dm_low_14 = dm_low_series.rolling(ref, min_periods=1).sum()

    di_high = 100 * (dm_high_14 / tr14)
    di_low = 100 * (dm_low_14 / tr14)

    dx = 100 * np.abs(di_high - di_low) / (di_high + di_low)

    adx = dx.rolling(ref, min_periods=1).mean()

    conf_buy_adx = ((adx > adx.shift(2)) | (adx > 50)) & (di_high > di_high.shift(2)) & (di_low < di_low.shift(2)) & (di_high > adx) & (adx < 70)
    conf_sell_adx = (((adx < 50) & (di_low < di_low.shift(1)) |(adx > 70) & (di_low < di_low.shift(1))) & (di_low > di_low.shift(1)) & (adx < adx.shift(1))) | (di_low > adx)

    return pd.DataFrame({'di_high': di_high, 'di_low': di_low, "adx": adx, "adx_buy_conf": conf_buy_adx,
                         "adx_sell_conf": conf_sell_adx})
