import pandas as pd
import numpy as np

def __getEdenSetup__(history, short_mav=8, long_mav=80):
    # Cálculo das médias móveis com base no logaritmo do fechamento
    log_close = np.log(history['Close'])
    mav_8 = log_close.rolling(window=short_mav).mean()
    mav_80 = log_close.rolling(window=long_mav).mean()

    # Retorna as médias móveis para a escala original
    mav_8_exp = np.exp(mav_8)
    mav_80_exp = np.exp(mav_80)

    # Condições para o setup Eden
    eden = ((history['Close'] > mav_8_exp) & (history['Close'] > mav_80_exp)) & \
           ((mav_8 > mav_8.shift(1)) & (mav_80 > mav_80.shift(1)))

    # Padrões adicionais
    inside_bar = (history['High'] < history['High'].shift(1)) & (history['Low'] > history['Low'].shift(1))
    red_bar = (history['Close'].shift(1) < history['Close'].shift(2)) & (history['Close'] > history['Close'].shift(1))

    # Sinais de compra e venda
    eden_buy_signal = eden & red_bar & inside_bar
    eden_sell_signal = history['Close'] <= mav_8_exp

    # Retorna um DataFrame com os indicadores e sinais
    return pd.DataFrame({
        'Mav_8': mav_8_exp,            # Escala original
        'Mav_80': mav_80_exp,          # Escala original
        'Eden_Buy_Signal': eden_buy_signal,
        'Eden_Sell_Signal': eden_sell_signal
    })
