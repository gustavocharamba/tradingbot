import pandas as pd


def __getBollinger__(history, ref):
    ma = history['Close'].rolling(window=ref).mean()
    std = history['Close'].rolling(window=ref).std()

    high_band = ma + 2 * std
    low_band = ma - 2 * std

    conf_buy_boll = (high_band > high_band.shift(1)) & (low_band < low_band.shift(1))
    conf_sell_boll = (high_band < high_band.shift(1)) & (low_band > low_band.shift(1))

    return pd.DataFrame({'high_band': high_band, 'low_band': low_band, 'boll_buy_conf': conf_buy_boll,
                         'boll_sell_conf': conf_sell_boll})
