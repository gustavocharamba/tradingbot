import plotly.graph_objects as go
from plotly.subplots import make_subplots

def __getGraph__(history, macd, rsi, ichimoku, executed_buy_signals, executed_sell_signals):
    """
    Creates a plot with Candlestick, MACD, RSI, and executed Buy/Sell signals in subplots.
    Ichimoku will be plotted in a separate subplot.
    """

    # Create figure with 4 subplots: Candlestick with executed Buy/Sell signals, MACD, RSI, Ichimoku
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=("", "MACD", "RSI", "Ichimoku Cloud")
    )

    # ============================== >>> Candlestick with Executed Buy/Sell Signals <<< ==============================
    fig.add_trace(go.Candlestick(
        x=history.index,
        open=history['Open'],
        high=history['High'],
        low=history['Low'],
        close=history['Close'],
        name='Candles'
    ), row=1, col=1)

    # Plot only executed Buy signals
    fig.add_trace(go.Scatter(
        x=executed_buy_signals.index,
        y=executed_buy_signals['Close'],
        mode='markers',
        name='Executed Buy Signal',
        marker=dict(symbol='triangle-up', color='green', size=10)
    ), row=1, col=1)

    # Plot only executed Sell signals
    fig.add_trace(go.Scatter(
        x=executed_sell_signals.index,
        y=executed_sell_signals['Close'],
        mode='markers',
        name='Executed Sell Signal',
        marker=dict(symbol='triangle-down', color='red', size=10)
    ), row=1, col=1)

    # ============================== >>> MACD <<< ==============================
    fig.add_trace(go.Scatter(
        x=history.index,
        y=macd['MACD'],
        mode='lines',
        name='MACD',
        line=dict(color='yellow')
    ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=history.index,
        y=macd['Signal_Line'],
        mode='lines',
        name='Signal Line',
        line=dict(color='white')
    ), row=2, col=1)

    fig.add_trace(go.Bar(
        x=history.index,
        y=macd['MACD_Histogram'],
        name='Histogram',
        marker_color=['green' if val >= 0 else 'red' for val in macd['MACD_Histogram']]
    ), row=2, col=1)

    # ============================== >>> RSI <<< ================================
    fig.add_trace(go.Scatter(
        x=history.index,
        y=rsi['RSI'],
        mode='lines',
        name='RSI',
        line=dict(color='blue')
    ), row=3, col=1)

    fig.add_trace(go.Scatter(
        x=history.index,
        y=rsi['RSI_Signal'],
        mode='lines',
        name='RSI Signal',
        line=dict(color='orange')
    ), row=3, col=1)

    # ============================== >>> Ichimoku Cloud <<< ==============================
    fig.add_trace(go.Scatter(
        x=history.index,
        y=ichimoku['Senkou_Span_A'],
        line=dict(color='rgba(0, 255, 0, 0.5)', width=1),
        name='Senkou Span A',
        fill='tonexty',
        mode='lines'
    ), row=4, col=1)

    fig.add_trace(go.Scatter(
        x=history.index,
        y=ichimoku['Senkou_Span_B'],
        line=dict(color='rgba(255, 0, 0, 0.5)', width=1),
        name='Senkou Span B',
        mode='lines'
    ), row=4, col=1)

    fig.add_trace(go.Scatter(
        x=history.index,
        y=ichimoku['Tenkan_sen'],
        line=dict(color='blue', width=1),
        name='Tenkan Sen'
    ), row=4, col=1)

    fig.add_trace(go.Scatter(
        x=history.index,
        y=ichimoku['Kijun_sen'],
        line=dict(color='orange', width=1),
        name='Kijun Sen'
    ), row=4, col=1)

    # ============================== >>> Layout <<< ==============================
    fig.update_layout(
        title='BTC/USD with Ichimoku, MACD, and RSI',
        template='plotly_dark',
        height=1400,  # Adjusted height for 4 subplots
        xaxis_rangeslider_visible=False,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # Configure y-axes titles
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="MACD", row=2, col=1)
    fig.update_yaxes(title_text="RSI", row=3, col=1)
    fig.update_yaxes(title_text="Ichimoku Cloud", row=4, col=1)

    # Configure x-axis title
    fig.update_xaxes(title_text="Date", row=4, col=1)

    # Show the figure
    fig.show()
