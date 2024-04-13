import pandas as pd

def __getEdenSetup__(history, period, short, long):
    history_subset = history.iloc[-period:]

    mav_8 = history_subset['Close'].rolling(window=short).mean()
    mav_80 = history_subset['Close'].rolling(window=long).mean()

    eden = (history_subset['Close'] > mav_8) & (history_subset['Close'] > mav_80)
    inside_bar = (history_subset['High'] < history_subset['High'].shift(1)) & (history_subset['Low'] > history_subset['Low'].shift(1))

    eden_buy_conf = eden & inside_bar

    return pd.DataFrame({'mav8': mav_8, 'mav80': mav_80, 'eden_buy_conf': eden_buy_conf})
