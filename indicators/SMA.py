import pandas as pd

def __getSMA__(history):

    sma_9 = history["Close"].rolling(window = 9).mean()
    sma_21 = history["Close"].rolling(window = 21).mean()
    sma_200 = history["Close"].rolling(window = 200).mean()

    return pd.DataFrame({"SMA_9": sma_9, "SMA_21": sma_21, "SMA_200": sma_200})