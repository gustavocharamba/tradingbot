import pandas as pd

def __getEdenSetup__(history, short, long):

    mav_8 = history['Close'].rolling(window=short).mean()
    mav_80 = history['Close'].rolling(window=long).mean()

    eden = (history['Close'] > mav_8) & (history['Close'] > mav_80)
    inside_bar = (history['High'] < history['High'].shift(1)) & (history['Low'] > history['Low'].shift(1))

    eden_buy_conf = eden & inside_bar

    return pd.DataFrame({'mav8': mav_8, 'mav80': mav_80, 'eden_buy_conf': eden_buy_conf})
