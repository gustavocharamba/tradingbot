import pandas as pd
import numpy as np

def __getMavLog__(history, median):

    log_close = np.log(history['Close'])
    log_mav_9 = log_close.rolling(window=median).mean()

    mav9_buy_conf = (log_mav_9 > log_mav_9.shift(1)) & (log_mav_9.shift(1) < log_mav_9.shift(2))
    mav9_sell_conf = (log_mav_9 < log_mav_9.shift(1)) & (log_mav_9.shift(1) > log_mav_9.shift(2))

    return pd.DataFrame({'log_mav_9': log_mav_9, 'mav9_buy_conf': mav9_buy_conf, 'mav9_sell_conf': mav9_sell_conf})
