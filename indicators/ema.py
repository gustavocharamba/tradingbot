import pandas as pd
import numpy as np

def __getEma__(history, median):

    log_close = np.log(history['Close'])
    ema = log_close.rolling(window=median).mean()

    ema_buy_conf = (ema > ema.shift(1)) & (ema.shift(1) < ema.shift(2))
    ema_sell_conf = (ema < ema.shift(1)) & (ema.shift(1) > ema.shift(2))

    return pd.DataFrame({'ema': ema, 'mav9_buy_conf': ema_buy_conf, 'mav9_sell_conf': ema_sell_conf})
