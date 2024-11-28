import pandas as pd

def __getMACD__(history, short=12, long=26, ref=9):

    short_ema = history['Close'].ewm(span=short, adjust=False).mean()
    long_ema = history['Close'].ewm(span=long, adjust=False).mean()

    # Calcula MACD e linha de referência
    macd = short_ema - long_ema
    macd_ref = macd.ewm(span=ref, adjust=False).mean()

    # Calcula o histograma
    macd_histogram = macd - macd_ref

    # Condição de compra: histograma acima de zero e aumentando
    macd_buy_conf = (
            (macd > macd_ref) &  # Cruzamento positivo
            (macd.shift(1) <= macd_ref.shift(1)) &  # MACD estava abaixo antes
            (macd_histogram > macd_histogram.shift(1)) &  # Histograma está aumentando
            (macd > 0)  # MACD está em território positivo
    )

    # Retorna o DataFrame com os resultados
    return pd.DataFrame({
        'MACD': macd,
        'MACD_Ref': macd_ref,
        'MACD_Histogram': macd_histogram,
        'MACD_Buy_Conf': macd_buy_conf
    })
