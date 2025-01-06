import pandas as pd

def __MACD__(history, short_period=12, long_period=26):
    # Calcular as EMAs de 12 e 26 períodos
    ema_12 = history["Close"].ewm(span=short_period, adjust=False).mean()
    ema_26 = history["Close"].ewm(span=long_period, adjust=False).mean()

    # Calcular o MACD
    macd = ema_12 - ema_26

    # Calcular a linha de sinal
    signal_ema = macd.ewm(span=9, adjust=False).mean()

    # Calcular o histograma
    histogram = (macd - signal_ema).squeeze()

    # Sinais de compra e venda
    macd_buy_conf = (macd > signal_ema) & (macd.shift(1) <= signal_ema.shift(1))  # Sinal de compra
    macd_sell_conf = (macd < signal_ema) & (macd.shift(1) >= signal_ema.shift(1))  # Sinal de venda

    return pd.DataFrame({
        "MACD": macd,
        "Signal_Line": signal_ema,
        "MACD_Histogram": histogram,
        "MACD_Buy_Conf": macd_buy_conf,
        "MACD_Sell_Conf": macd_sell_conf
    })
