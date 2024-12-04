import pandas as pd
import yfinance as yf
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler

from tradingbot.indicators.macd import __getMACD__
from tradingbot.indicators.rsi import __getRSI__
from tradingbot.indicators.ichimoku import __getIchimoku__
from tradingbot.indicators.obv import __getOBV__
from tradingbot.indicators.PSAR import __getParabolicSAR__

# Baixando os dados históricos do BTC
btc_data = yf.Ticker("BTC-USD")
history = btc_data.history(period="2y", interval="1h")  # 2 anos de dados

# Obtendo os indicadores
macd = __getMACD__(history)
rsi = __getRSI__(history)
ichimoku = __getIchimoku__(history)
obv = __getOBV__(history)
psar = __getParabolicSAR__(history)

# Concatenando os sinais de compra em um único DataFrame
data = pd.concat([macd, rsi, ichimoku, obv, psar], axis=1)

# Definindo o alvo: 1 para compra, 0 para nenhuma ação
data['Target'] = 0  # Inicializa com 0, que é "nenhuma ação"

# Ajustando para 1 quando qualquer indicador sugerir compra
data.loc[macd['MACD_Buy_Conf'] == 1, 'Target'] = 1
data.loc[rsi['RSI_Buy_Conf'] == 1, 'Target'] = 1
data.loc[ichimoku['Ichimoku_Buy_Conf'] == 1, 'Target'] = 1
data.loc[obv['OBV_Buy_Conf'] == 1, 'Target'] = 1
data.loc[psar['ParabolicSAR_Buy_Conf'] == 1, 'Target'] = 1

# Garantindo que o conjunto de dados tenha pelo menos alguns exemplos com Target == 0
print(data.head())

# Definindo X (features) e y (target)
X = data.drop(columns=['Target'])
y = data['Target']

# Verificando o balanceamento do Target
print(y.value_counts())  # Isso vai mostrar quantos 1 e quantos 0 existem

# Dividindo os dados em treino e teste (80% treino, 20% teste)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Padronizando os dados
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Treinando o modelo XGBoost
model = XGBClassifier()
model.fit(X_train_scaled, y_train)

# Avaliando o modelo
y_pred = model.predict(X_test_scaled)
print(classification_report(y_test, y_pred))

# Agora, simulando os trades

# Prevendo as ações para o histórico
data['Predictions'] = model.predict(scaler.transform(X))  # Previsões para o conjunto completo

# Inicializando variáveis de simulação
cash = 10000  # Valor inicial em dinheiro
btc_balance = 0  # Quantidade de BTC comprada
buy_price = 0  # Preço de compra do BTC
trade_history = []  # Histórico de trades

# Simulando os trades
for i in range(1, len(data)):
    # Se o modelo prevê comprar e temos dinheiro suficiente
    if data['Predictions'].iloc[i] == 1 and cash > 0:
        buy_price = history['Close'].iloc[i]
        btc_balance = cash / buy_price  # Compramos BTC
        cash = 0  # Não temos mais dinheiro disponível
        trade_history.append(('BUY', history.index[i], buy_price))

    # Se o modelo prevê não comprar e temos BTC, vendemos
    elif data['Predictions'].iloc[i] == 0 and btc_balance > 0:
        sell_price = history['Close'].iloc[i]
        cash = btc_balance * sell_price  # Vendemos o BTC
        btc_balance = 0  # Não temos mais BTC
        trade_history.append(('SELL', history.index[i], sell_price))

# Calculando o saldo final
final_balance = cash + (btc_balance * history['Close'].iloc[-1])

# Exibindo o resultado da simulação
print(f'Balanço final: ${final_balance:.2f}')
print(f'Número de trades realizados: {len(trade_history)}')
print('Histórico de trades:')
for trade in trade_history:
    print(trade)

