import pandas as pd


def __getTrix__(history, short, long):

    ema1 = history['Close'].ewm(span=long, adjust=False).mean()
    ema2 = ema1.ewm(span=long, adjust=False).mean()
    ema3 = ema2.ewm(span=long, adjust=False).mean()

    trix = 100 * ema3.pct_change()
    trix_sma = trix.rolling(window=short).mean()

    trix_buy_conf = (trix > trix_sma)

    trix_sell_conf = (trix < trix_sma)

    return pd.DataFrame(
        {'trix': trix, 'trix_sma': trix_sma, 'trix_buy_conf': trix_buy_conf, 'trix_sell_conf': trix_sell_conf})
