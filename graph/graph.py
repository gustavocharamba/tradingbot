import plotly.graph_objects as go
from plotly.subplots import make_subplots


def __getGraph__(history, macd, stoch, trix, rsi):
    """
    Creates a plot with Candlestick, MACD, Stochastic, TRIX, and RSI indicators in separate subplots.

    Parameters:
    - history (pd.DataFrame): Historical price data.
    - macd (pd.DataFrame): MACD indicators.
    - stoch (pd.DataFrame): Stochastic indicators.
    - trix (pd.DataFrame): TRIX indicators.
    - rsi (pd.DataFrame): RSI indicators.
    """

    # Create figure with 5 subplots: Candlestick, MACD, Stochastic, TRIX, RSI
    fig = make_subplots(
        rows=5, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=("Candlestick", "MACD", "Stochastic", "TRIX", "RSI")
    )

    # ============================== >>> Candlestick <<< ==============================
    fig.add_trace(go.Candlestick(
        x=history.index,
        open=history['Open'],
        high=history['High'],
        low=history['Low'],
        close=history['Close'],
        name='Candles'
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
        y=macd['MACD_Ref'],
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

    # ============================== >>> Stochastic <<< ==============================
    fig.add_trace(go.Scatter(
        x=history.index,
        y=stoch['K_Line'],
        mode='lines',
        name='K Line',
        line=dict(color='green')
    ), row=3, col=1)

    fig.add_trace(go.Scatter(
        x=history.index,
        y=stoch['D_Line'],
        mode='lines',
        name='D Line (Signal)',
        line=dict(color='white')
    ), row=3, col=1)

    # ============================== >>> TRIX <<< ================================
    fig.add_trace(go.Scatter(
        x=history.index,
        y=trix['TRIX'],
        mode='lines',
        name='TRIX',
        line=dict(color='green')
    ), row=4, col=1)

    fig.add_trace(go.Scatter(
        x=history.index,
        y=trix['TRIX_SMA'],
        mode='lines',
        name='TRIX SMA',
        line=dict(color='white')
    ), row=4, col=1)

    # ============================== >>> RSI <<< ================================
    fig.add_trace(go.Scatter(
        x=history.index,
        y=rsi['RSI'],
        mode='lines',
        name='RSI',
        line=dict(color='blue')
    ), row=5, col=1)

    fig.add_trace(go.Scatter(
        x=history.index,
        y=rsi['RSI_Signal'],
        mode='lines',
        name='RSI Signal',
        line=dict(color='orange')
    ), row=5, col=1)

    # ============================== >>> Layout <<< ==============================
    fig.update_layout(
        title='BTC/USD',
        template='plotly_dark',
        height=1200,  # Increased height to accommodate all subplots
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
    fig.update_yaxes(title_text="Stochastic", row=3, col=1)
    fig.update_yaxes(title_text="TRIX", row=4, col=1)
    fig.update_yaxes(title_text="RSI", row=5, col=1)

    # Configure x-axis title
    fig.update_xaxes(title_text="Date", row=5, col=1)

    # Show the figure
    fig.show()
