import yfinance as yf
import pandas as pd
import plotly.graph_objs as go

def __getMACD__(history,short, long, ref):

    short_ema = history['Close'].ewm(span=short, adjust=False).mean()
    long_ema = history['Close'].ewm(span=long, adjust=False).mean()

    macd = short_ema - long_ema
    ref_line = macd.ewm(span=ref, adjust=False).mean()

    macd_histogram = macd - ref_line

    macd_buy_conf = (macd_histogram > macd_histogram.shift(1)) & (macd_histogram > 0)

    return pd.DataFrame({'macd_histogram': macd_histogram, 'macd_buy_conf': macd_buy_conf})

