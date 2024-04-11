import plotly.graph_objects as go
import plotly.subplots as subplots


def __getGraph__(history, period, didi, boll, adx, trix, stoch, oper_buy, oper_sell):
    fig = subplots.make_subplots(rows=5, cols=1, row_heights=[0.40, 0.15, 0.15, 0.15, 0.15])

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

    # ============================== >>> Bollinger <<< ==============================

    # conf_buy_boll = boll['boll_buy_conf'][-period:]
    # conf_sell_boll = boll['boll_sell_conf'][-period:]
    #
    # boll_cof_buy_prices = boll['high_band'][-period:][conf_buy_boll]
    # boll_cof_sell_prices = boll['low_band'][-period:][conf_sell_boll]
    #
    # fig.add_trace(go.Scatter(x=history.index[-period:], y=boll['high_band'][-period:], mode='lines', name='Low Band',
    #                          line=dict(color='grey')), row=1, col=1)
    # fig.add_trace(go.Scatter(x=history.index[-period:], y=boll['low_band'][-period:], mode='lines', name='High Band',
    #                          line=dict(color='grey')), row=1, col=1)
    # fig.add_trace(go.Scatter(x=boll_cof_buy_prices.index, y=boll_cof_buy_prices, mode='markers', name='Conf Buy Bollinger',
    #                          marker=dict(color='green', size=6)), row=1, col=1)
    # fig.add_trace(go.Scatter(x=boll_cof_sell_prices.index, y=boll_cof_sell_prices, mode='markers', name='Conf Sell Bollinger',
    #                          marker=dict(color='red', size=6)), row=1, col=1)


    # ============================== >>> Didi <<< ==================================

    didi_conf_buy = didi['didi_buy_conf'][-period:]
    didi_conf_sell = didi['didi_sell_conf'][-period:]

    didi_cof_buy_prices = didi['short_line'][-period:][didi_conf_buy] - didi['ref_line'][-period:][didi_conf_buy]
    didi_cof_sell_prices = didi['short_line'][-period:][didi_conf_sell] - didi['ref_line'][-period:][didi_conf_sell]

    fig.add_trace(go.Scatter(x=history.index[-period:], y=(didi['short_line'][-period:] - didi['ref_line'][-period:]),
                             mode='lines', name='Short',
                             line=dict(color='green')), row=2, col=1)
    fig.add_trace(go.Scatter(x=history.index[-period:], y=(didi['long_line'][-period:] - didi['ref_line'][-period:]),
                             mode='lines', name='Long',
                             line=dict(color='red')), row=2, col=1)
    fig.add_trace(go.Scatter(x=didi_cof_buy_prices.index[-period:], y=didi_cof_buy_prices[-period:], mode='markers', name='Conf Buy Didi',
                             marker=dict(color='blue', size=6)), row=2, col=1)
    fig.add_trace(go.Scatter(x=didi_cof_sell_prices.index[-period:], y=didi_cof_sell_prices[-period:], mode='markers', name='Conf Sell Didi',
                             marker=dict(color='yellow', size=6)), row=2, col=1)

    # ============================== >>> ADX <<< ===================================

    adx_conf_buy = adx['adx_buy_conf'][-period:]
    adx_conf_sell = adx['adx_sell_conf'][-period:]

    adx_cof_buy_prices = adx['adx'][-period:][adx_conf_buy]
    adx_cof_sell_prices = adx['adx'][-period:][adx_conf_sell]

    fig.add_trace(go.Scatter(x=history.index[-period:], y=(adx['di_low'][-period:]), mode='lines', name='-DI',
                             line=dict(color='red')), row=3, col=1)
    fig.add_trace(go.Scatter(x=history.index[-period:], y=(adx['di_high'][-period:]), mode='lines', name='+DI',
                             line=dict(color='green')), row=3, col=1)
    fig.add_trace(go.Scatter(x=history.index[-period:], y=(adx['adx'][-period:]), mode='lines', name='ADX',
                             line=dict(color='white')), row=3, col=1)
    fig.add_trace(go.Scatter(x=adx_cof_buy_prices.index, y=adx_cof_buy_prices, mode='markers', name='Conf Buy ADX',
                             marker=dict(color='blue', size=6)), row=3, col=1)
    fig.add_trace(go.Scatter(x=adx_cof_sell_prices.index, y=adx_cof_sell_prices, mode='markers', name='Conf Sell ADX',
                             marker=dict(color='yellow', size=6)), row=3, col=1)

    # ============================== >>> Trix <<< ===================================

    conf_buy_trix = trix['trix_buy_conf'][-period:]
    conf_sell_trix = trix['trix_sell_conf'][-period:]

    conf_buy_trix_prices = trix['trix'][-period:][conf_buy_trix]
    conf_sell_trix_prices = trix['trix_sma'][-period:][conf_sell_trix]

    fig.add_trace(go.Scatter(x=history.index[-period:], y=trix['trix'][-period:], mode='lines', name='Trix', marker=dict(color='green')), row=4, col=1)
    fig.add_trace(go.Scatter(x=history.index[-period:], y=trix['trix_sma'][-period:], mode='lines', name='Trix Ref', marker=dict(color='white')), row=4, col=1)
    fig.add_trace(go.Scatter(x=conf_buy_trix_prices.index[-period:], y=conf_buy_trix_prices[-period:], mode='markers', name='Trix Buy Conf',
                             marker=dict(color='blue', size=6)), row=4, col=1)
    fig.add_trace(go.Scatter(x=conf_sell_trix_prices.index[-period:], y=conf_sell_trix_prices[-period:], mode='markers', name='Trix Sell Conf',
                             marker=dict(color='yellow', size=6)), row=4, col=1)

    # ============================== >>> Stochastic <<< =============================

    conf_buy_stoch = stoch['stoch_buy_conf'][-period:]
    conf_sell_stoch = stoch['stoch_sell_conf'][-period:]

    conf_buy_stoch_prices = stoch['k_line'][-period:][conf_buy_stoch]
    conf_sell_stoch_prices = stoch['k_line'][-period:][conf_sell_stoch]

    fig.add_trace(go.Scatter(x=history.index[-period:], y=stoch['k_line'][-period:], mode='lines', name='Stoch',
                             marker=dict(color='green')), row=5, col=1)
    fig.add_trace(go.Scatter(x=history.index[-period:], y=stoch['d_line'][-period:], mode='lines', name='Stoch Ref',
                             marker=dict(color='white')), row=5, col=1)
    fig.add_trace(go.Scatter(x=conf_buy_stoch_prices.index[-period:], y=conf_buy_stoch_prices[-period:], mode='markers', name='Stoch Buy Conf',
                             marker=dict(color='blue', size=6)), row=5, col=1)
    fig.add_trace(go.Scatter(x=conf_sell_stoch_prices.index[-period:], y=conf_sell_stoch_prices[-period:], mode='markers', name='Stoch Sell Conf',
                             marker=dict(color='yellow', size=6)), row=5, col=1)

    # ===============================================================================
    fig.update_layout(title='BTC/USD',
                      xaxis_title='Date',
                      yaxis_title='Price ($)',
                      template='plotly_dark',
                      xaxis={"rangeslider": {"visible": False}})

    config = {'scrollZoom': True}

    fig.show(config=config)
