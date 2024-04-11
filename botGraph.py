import plotly.graph_objects as go
import plotly.subplots as subplots
from datetime import date

def __getBotGraph__(history, period, oper_buy, oper_sell):
    fig = subplots.make_subplots(rows=1, cols=1)

    # ============================== >>> Candles <<< ==============================

    fig.add_trace(go.Candlestick(x=history.index[-period:],
                                 open=history['Open'][-period:],
                                 high=history['High'][-period:],
                                 low=history['Low'][-period:],
                                 close=history['Close'][-period:]), row=1, col=1)

    # ============================== >>> Buy/Sell <<< ==============================

    buy_dates = history.index[-period:][oper_buy[-period:]]
    buy_prices = history['Close'][-period:][oper_buy[-period:]]

    sell_dates = history.index[-period:][oper_sell[-period:]]
    sell_prices = history['Close'][-period:][oper_sell[-period:]]

    fig.add_trace(go.Scatter(x=buy_dates, y=buy_prices, mode='markers', name='Compra',
                             marker=dict(color='blue', size=6)), row=1, col=1)

    fig.add_trace(go.Scatter(x=sell_dates, y=sell_prices, mode='markers', name='Venda',
                             marker=dict(color='yellow', size=6)), row=1, col=1)

    fig.update_layout(title='BTC/USD',
                      xaxis_title='Date',
                      yaxis_title='Price ($)',
                      template='plotly_dark',
                      xaxis={"rangeslider": {"visible": False}})

    config = {'scrollZoom': True}

    fig.show(config=config)


