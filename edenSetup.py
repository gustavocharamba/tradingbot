import pandas as pd
import numpy as np

def __getEdenSetup__(history):
    data = history['Close']

    mav8 = data.rolling(window=8).mean()
    mav80 = data.rolling(window=80).mean()

    eden_buy_conf = (data > mav8 & data > mav80)

    return 0