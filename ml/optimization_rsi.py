import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
from tradingbot.indicators.rsi import __getRSI__

# Carregar os dados
data = pd.read_csv("../datas/BTC1H2018-2024.csv")

# Calcular o RSI
rsi = __getRSI__(data, 14)

# Adicionar RSI aos dados
data['RSI'] = rsi['RSI']

# Filtrar colunas desnecessárias
filter = ['Close time', 'Quote asset volume', 'Number of trades',
          'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']
data = data.drop(filter, axis=1)

# Criar a coluna 'Trade' com base no critério de bom trade (5% de aumento em 4 candles)
trade = []
for i in range(len(data) - 96):  # Garantir que há pelo menos 10 candles à frente
    # Verificar se o preço de fechamento do candle 10 posições à frente é 5% maior
    if data['Close'].iloc[i + 96] >= data['Close'].iloc[i] * 1.05:
        trade.append(1)  # Considerado um bom trade
    else:
        trade.append(0)  # Não é um bom trade

# Adicionar a coluna 'Trade' aos dados
data['Trade'] = np.concatenate([np.zeros(96), np.array(trade)])  # Adiciona 10 zeros no início

# Inicializar listas para armazenar as médias do RSI e MSE das iterações
rsi_means = []
mse_values = []

# Loop pelas 30 iterações
for i in range(30):
    # Definir o período
    start_idx = np.random.randint(0, len(data) - 360)
    end_idx = start_idx + 360

    # Extrair os dados de treino para cada iteração
    train_data = data.iloc[start_idx:end_idx]

    # Filtrar os valores do RSI quando Trade == 1
    rsi_values_trade_1 = train_data[train_data['Trade'] == 1]['RSI']

    # Verificar se existem valores válidos para Trade == 1
    if not rsi_values_trade_1.empty:
        rsi_mean = rsi_values_trade_1.mean()
        rsi_means.append(rsi_mean)

        # Calcular MSE - Previsão: se RSI for menor que 30, previsão é compra (Trade == 1), senão é 0
        y_true = train_data['Trade']
        y_pred = (train_data['RSI'] < 30).astype(int)  # Supondo que o RSI abaixo de 30 é um sinal de compra

        mse = mean_squared_error(y_true, y_pred)
        mse_values.append(mse)
    else:
        print(f"Iteração {i}: Não há valores de RSI com Trade == 1")

# Calcular a média do RSI nas 30 iterações com Trade == 1
if rsi_means:
    mean_rsi = np.mean(rsi_means)
    print(f"Média do RSI nas 30 iterações com Trade == 1: {mean_rsi}")
else:
    print("Não há valores de RSI com Trade == 1 nas 30 iterações.")

# Calcular a média do MSE
if mse_values:
    mean_mse = np.mean(mse_values)
    print(f"Média do MSE nas 30 iterações: {mean_mse}")
else:
    print("Não foi possível calcular o MSE nas 30 iterações.")

# Plotar as médias do RSI por iteração
plt.figure(figsize=(10, 6))
plt.subplot(2, 1, 1)
plt.plot(rsi_means, label="Média RSI por iteração", color='blue')
plt.axhline(y=mean_rsi, color='r', linestyle='--', label="Média Geral RSI")
plt.xlabel("Iterações")
plt.ylabel("Média RSI")
plt.title("Média do RSI nas 30 iterações com Trade == 1")
plt.legend()

# Plotar o MSE por iteração
plt.subplot(2, 1, 2)
plt.plot(mse_values, label="MSE por iteração", color='green')
plt.axhline(y=mean_mse, color='orange', linestyle='--', label="Média Geral MSE")
plt.xlabel("Iterações")
plt.ylabel("MSE")
plt.title("Média do MSE nas 30 iterações")
plt.legend()

plt.tight_layout()
plt.show()
