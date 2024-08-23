import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from datetime import datetime, timedelta
from dash import Dash, dcc, html, Input, Output

# Definește data curentă și data de început
end_date = datetime.now()
start_date = end_date - timedelta(days=36500)  # Ultimii 100 de ani pentru a acoperi toate perioadele

# Creează aplicația Dash
app = Dash(__name__)

# Layout-ul aplicației
app.layout = html.Div([
    html.H1('Stock Price Evolution'),

    # Text box pentru simbolul bursier și butonul de căutare
    html.Div([
        dcc.Input(id='stock-symbol', type='text', value='AAPL', style={'marginRight': '10px'}),
        html.Button('Search Stock', id='search-button', n_clicks=0)
    ], style={'marginBottom': '20px'}),

    # Graficul va fi actualizat aici
    dcc.Graph(id='stock-graph')
])

@app.callback(
    Output('stock-graph', 'figure'),
    Input('search-button', 'n_clicks'),
    Input('stock-symbol', 'value')
)
def update_graph(n_clicks, symbol):
    if not symbol:
        symbol = 'AAPL'
    
    try:
        # Descarcă datele pentru simbolul bursier
        df = yf.download(symbol, start=start_date, end=end_date)
        if df.empty:
            raise ValueError("No data found for the symbol")
        
        df['Date'] = df.index.date
        df['Close'] = df['Close'].round(2)
        df['Open'] = df['Open'].round(2)
        df['High'] = df['High'].round(2)
        df['Low'] = df['Low'].round(2)
        df['Volume'] = df['Volume'].apply(lambda x: f"{x:,}")
        df['Symbol'] = symbol

        # Obține informațiile despre companie
        ticker = yf.Ticker(symbol)
        stock_info = ticker.info

        company_name = stock_info.get('shortName', symbol)  # Folosește simbolul dacă numele nu este disponibil
        last_close_price = df['Close'].iloc[-1] if not df['Close'].empty else 'N/A'
        last_close_date = df['Date'].iloc[-1] if not df['Date'].empty else 'N/A'

        # Convertim datele într-un format ușor de afișat
        last_close_price_str = f"{last_close_price:.2f}" if isinstance(last_close_price, (int, float)) else last_close_price
        last_close_date_str = last_close_date.strftime('%Y-%m-%d') if isinstance(last_close_date, datetime) else last_close_date

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Close'],
            mode='lines+markers',
            name=f'{symbol} - Preț de Închidere',
            marker=dict(size=8),
            text=[f"Date: {date}<br>Close: {close:.2f}<br>Open: {open:.2f}<br>High: {high:.2f}<br>Low: {low:.2f}<br>Volume: {volume}<br>Symbol: {symbol}" 
                  for date, close, open, high, low, volume in zip(df['Date'], df['Close'], df['Open'], df['High'], df['Low'], df['Volume'])],
            hoverinfo='text'
        ))

        fig.update_layout(
            title=(f'Price evolution for {company_name} ({symbol}) - '
                   f'Last Close: {last_close_price_str} on {last_close_date_str} - '
                   f'Exchange: NASDAQ'),
            xaxis=dict(tickformat='%Y-%m-%d'),
            updatemenus=[
                dict(
                    buttons=[
                        dict(
                            args=[{'xaxis.range': [df['Date'].max() - timedelta(days=5), df['Date'].max()]}],
                            label="5D",
                            method="relayout"
                        ),
                        dict(
                            args=[{'xaxis.range': [df['Date'].max() - timedelta(days=30), df['Date'].max()]}],
                            label="1M",
                            method="relayout"
                        ),
                        dict(
                            args=[{'xaxis.range': [df['Date'].max() - timedelta(days=93), df['Date'].max()]}],
                            label="3M",
                            method="relayout"
                        ),
                        dict(
                            args=[{'xaxis.range': [df['Date'].max() - timedelta(days=182), df['Date'].max()]}],
                            label="6M",
                            method="relayout"
                        ),
                        dict(
                            args=[{'xaxis.range': [df['Date'].max() - timedelta(days=365), df['Date'].max()]}],
                            label="1Y",
                            method="relayout"
                        ),
                        dict(
                            args=[{'xaxis.range': [df['Date'].max() - timedelta(days=1825), df['Date'].max()]}],
                            label="5Y",
                            method="relayout"
                        ),
                        dict(
                            args=[{'xaxis.range': [df['Date'].min(), df['Date'].max()]}],
                            label="All",
                            method="relayout"
                        )
                    ],
                    direction="left",
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    type="buttons",
                    x=0.1,
                    xanchor="left",
                    y=1.15,
                    yanchor="top"
                ),
                dict(
                    type="buttons",
                    direction="left",
                    buttons=[dict(
                        label="Markers On/Off",
                        method="restyle",
                        args=["mode", "lines+markers"],  # Toggle între "lines" și "lines+markers"
                        args2=["mode", "lines"],  # A doua stare a butonului
                    )],
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0.48,  # Mută butonul mai la dreapta
                    xanchor="left",
                    y=1.15,
                    yanchor="top"
                ),
            ]
        )

    except Exception as e:
        # Dacă există o eroare, arată un grafic gol cu mesajul de eroare
        fig = go.Figure()
        fig.update_layout(
            title=f'Error: {str(e)}',
            xaxis=dict(tickformat='%Y-%m-%d')
        )

    return fig

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=10000, debug=True)

