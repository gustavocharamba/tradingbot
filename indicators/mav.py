import pandas as pd

def __getMAV__(history, period, short, long):
    history_subset = history.iloc[-period:]

    mav_short = history_subset['Close'].rolling(window=short).mean()
    mav_long = history_subset['Close'].rolling(window=long).mean()

    mav_buy_conf = (mav_short > mav_long) & (mav_short.shift(1) <= mav_long.shift(1))
    mav_sell_conf = (mav_short < mav_long) & (mav_short.shift(1) >= mav_long.shift(1))

    return pd.DataFrame({'mav_short': mav_short, 'mav_long': mav_long,
                         'mav_buy_conf': mav_buy_conf, 'mav_sell_conf': mav_sell_conf})
