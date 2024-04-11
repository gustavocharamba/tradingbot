import pandas as pd


def __getDidi__(history, short, long, ref):

    short_line = history['Close'].rolling(window=short).mean()
    long_line = history['Close'].rolling(window=long).mean()
    ref_line = history['Close'].rolling(window=ref).mean()

    #didi_buy_conf = (short_line > long_line.shift(1)) & (short_line > long_line) & (short_line > ref_line) & (short_line.shift(1) < long_line.shift(1))
    didi_buy_conf = (short_line > short_line.shift(3)) & (short_line > long_line) & (short_line > ref_line)
    didi_sell_conf = (long_line > long_line.shift(3)) & (long_line > short_line) & (long_line < ref_line)

    return pd.DataFrame({'short_line': short_line, 'long_line': long_line, 'ref_line': ref_line,
                         'didi_buy_conf': didi_buy_conf, 'didi_sell_conf': didi_sell_conf})
