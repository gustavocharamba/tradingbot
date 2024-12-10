def execute_trades(strategy_type):
    position = None  # None ou 'buy'
    buy_price = 0
    profits = []
    current_balance = initial_balance
    btc_quantity = 0

    for i in range(len(training_data)):
        if strategy_type == "ml":
            # Extrair as features como um DataFrame com os mesmos nomes de colunas usados no treinamento
            features = training_data.iloc[i:i+1][X.columns].values  # Converte para NumPy array
            prediction = model.predict(features)[0]  # Previsão do modelo
        elif strategy_type == "indicators":
            # Estratégia baseada em indicadores
            prediction = indicator_based_strategy(training_data.iloc[i])

        # Lógica de compra e venda
        if prediction == 1 and position is None:  # Sinal de compra
            trade_value = current_balance * trade_size
            btc_quantity = trade_value / training_data['Close'].iloc[i]
            position = 'buy'
            buy_price = training_data['Close'].iloc[i]
            current_balance -= trade_value

        elif prediction == 0 and position == 'buy':  # Sinal de venda
            sell_price = training_data['Close'].iloc[i]
            profit = (sell_price - buy_price) * btc_quantity
            current_balance += btc_quantity * sell_price
            profits.append(profit)
            position = None

    total_profit = sum(profits)
    final_balance = current_balance
    win_percentage = (sum(1 for profit in profits if profit > 0) / len(profits)) * 100 if profits else 0

    return total_profit, final_balance, win_percentage
