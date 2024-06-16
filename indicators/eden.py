import pandas as pd
import numpy as np
def __getEdenSetup__(history, short, long):

    log_close = np.log(history['Close'])
    mav_8 = log_close.rolling(window=short).mean()
    mav_80 = log_close.rolling(window=long).mean()

    eden = ((history['Close'] > mav_8) & (history['Close'] > mav_80)) &  ((mav_8 > mav_8.shift(1)) & (mav_80 > mav_80.shift(1)))
    inside_bar = (history['High'] < history['High'].shift(1)) & (history['Low'] > history['Low'].shift(1))

    eden_buy_conf = eden & inside_bar

    return pd.DataFrame({'mav8': mav_8, 'mav80': mav_80, 'eden_buy_conf': eden_buy_conf})
