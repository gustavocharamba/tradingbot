import pandas as pd
import numpy as np

def __getEMA__(history , short, long):

    log_close = np.log(history['Close'])
    ema_short = log_close.rolling(window=short).mean()
    ema_long = log_close.rolling(window=long).mean()

    ema_buy_conf = (ema_short > ema_long)
    ema_sell_conf = (ema_short < ema_long)

    return pd.DataFrame({'ema_buy_conf': ema_buy_conf, 'ema_sell_conf': ema_sell_conf})
