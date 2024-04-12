import pandas as pd


def __getStochastic__(history, short, long):
    low_min = history['Low'].rolling(window=long).min()
    high_max = history['High'].rolling(window=long).max()

    k_line = 100 * ((history['Close'] - low_min) / (high_max - low_min))

    d_line = k_line.rolling(window=short).mean()

    conf_buy_stoch = (k_line > d_line)
    conf_sell_stoch = (d_line > k_line)

    return pd.DataFrame({'k_line': k_line, 'd_line': d_line, 'stoch_buy_conf': conf_buy_stoch,'stoch_sell_conf': conf_sell_stoch})
