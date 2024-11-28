import pandas as pd


def __getTrix__(history, short=9, long=15):

    ema1 = history['Close'].ewm(span=long, adjust=False).mean()
    ema2 = ema1.ewm(span=long, adjust=False).mean()
    ema3 = ema2.ewm(span=long, adjust=False).mean()

    trix = 100 * ema3.pct_change()
    trix_sma = trix.rolling(window=short).mean()

    trix_buy_conf = (
        (trix > trix_sma) &  # TRIX está acima de sua SMA
        (trix > 0) &  # TRIX está em território positivo
        (trix > trix.shift(1)) &  # TRIX está em tendência crescente
        (trix > trix.shift(5))  # TRIX está acima do seu valor de 5 períodos atrás
    )


    return pd.DataFrame(
        {'TRIX': trix, 'TRIX_SMA': trix_sma, 'TRIX_Buy_Conf': trix_buy_conf})