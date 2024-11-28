import yfinance as yf

from trading.setup.eden import __getEdenSetup__

from trading.graph.graph import __getEdenGraph__

btc_data = yf.Ticker("BTC-USD")
history = btc_data.history(period="1y", interval="1d")

eden = __getEdenSetup__(history)

def __getTrade__(balance, amount, period):
    aportes = []  # Lista para armazenar operações de compra abertas

    oper_buy = [False] * history.shape[0]  # Marca operações de compra
    oper_sell = [False] * history.shape[0]  # Marca operações de venda

    # Variável para rastrear se há uma posição aberta
    posicao_aberta = False

    for i in range(history['Close'][-period:].shape[0]):

        # Verifica o sinal de compra e se não há posição aberta
        if eden['Eden_Buy_Signal'].iloc[i] and balance >= amount and not posicao_aberta:
            price = history['Close'].iloc[i]
            oper_buy[i] = True

            # Calcula quantidade comprada e atualiza saldo
            quantity = amount / price
            aportes.append([quantity, price])
            balance -= amount

            # Marca que há uma posição aberta
            posicao_aberta = True

        # Verifica o sinal de venda e se há posição aberta
        if eden['Eden_Sell_Signal'].iloc[i] and posicao_aberta:
            price = history['Close'].iloc[i]
            oper_sell[i] = True

            for j in aportes:
                # Calcula lucro e atualiza saldo
                lucro = j[0] * price - j[0] * j[1]
                print(f"Lucro: {lucro:.2f}")
                balance += j[0] * price

            # Limpa operações abertas e marca posição como fechada
            aportes = []
            posicao_aberta = False

    # Atualiza gráfico com as operações realizadas
    __getEdenGraph__(history, eden, oper_buy, oper_sell)
    return balance, aportes, oper_buy, oper_sell


balance, aportes, oper_buy, oper_sell= __getTrade__(10000, 10000, -1)
print(f'BALANCE FINALIZADO: {balance}, APORTES FINALIZADOS: {aportes}')
