import pandas as pd


def __getStochastic__(history, short=3, long=14):
    """
    Calcula o Estocástico Lento (Slow Stochastic) para determinar sinais de compra.

    Parâmetros:
    - history (pd.DataFrame): Dados históricos de preços com colunas ['High', 'Low', 'Close'].
    - short (int): Período da média móvel de %K (linha %D). Padrão = 3.
    - long (int): Período para o cálculo da janela de máximo e mínimo. Padrão = 14.

    Retorno:
    - pd.DataFrame: Contém as colunas 'K_Line', 'D_Line' e 'STOCH_Buy_Conf' (sinal de compra).
    """

    # Calculando o mínimo e máximo no intervalo 'long'
    low_min = history['Low'].rolling(window=long).min()
    high_max = history['High'].rolling(window=long).max()

    # Calculando a linha %K
    k_line = 100 * ((history['Close'] - low_min) / (high_max - low_min))

    # Calculando a linha %D (média móvel de %K)
    d_line = k_line.rolling(window=short).mean()

    # Condição de compra: %K cruza acima de %D e %K > 20 (evita compras durante forte queda)
    conf_buy_stoch = (k_line > d_line) & (k_line.shift(1) <= d_line.shift(1)) & (k_line > 20)

    # Retorna as linhas %K, %D e a confirmação de compra
    return pd.DataFrame({
        'K_Line': k_line,
        'D_Line': d_line,
        'STOCH_Buy_Conf': conf_buy_stoch
    })
