import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from datetime import datetime, timedelta
from dash import Dash, dcc, html, Input, Output, ctx

# Definește data curentă și data de început
end_date = datetime.now()
start_date = end_date - timedelta(days=36500)  # Ultimii 100 de ani pentru a acoperi toate perioadele

# Creează aplicația Dash
app = Dash(__name__)

# Layout-ul aplicației
app.layout = html.Div([
    html.H1('Stock Price Evolution', style={'textAlign': 'center', 'marginBottom': '20px'}),

    # Text box pentru simbolul bursier și butonul de căutare
    html.Div([
        dcc.Input(id='stock-symbol', type='text', value='AAPL', style={'marginRight': '10px', 'width': '60%'}),
        html.Button('Search Stock', id='search-button', n_clicks=0, style={'width': '30%'})
    ], className='input-container', style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'marginBottom': '10px'}),

    # Butoanele de filtrare
    html.Div([
        html.Button('5D', id='button-5d', n_clicks=0),
        html.Button('1M', id='button-1m', n_clicks=0),
        html.Button('3M', id='button-3m', n_clicks=0),
        html.Button('6M', id='button-6m', n_clicks=0),
        html.Button('1Y', id='button-1y', n_clicks=0),
        html.Button('5Y', id='button-5y', n_clicks=0),
        html.Button('All', id='button-all', n_clicks=0),
        html.Button('Markers On/Off', id='button-markers', n_clicks=0),
    ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'center', 'marginBottom': '20px'}),

    # Graficul va fi actualizat aici
    dcc.Graph(
        id='stock-graph',
        config={'responsive': True},  # Asigură-te că graficul se ajustează automat
        style={'width': '100%', 'height': '70vh'}  # Ajustează înălțimea pentru a se potrivi mai bine
    ),

    # Stocarea stării markerilor
    dcc.Store(id='markers-state', data=True),  # True indică markerii activi inițial
    dcc.Store(id='current-range', data={'start': None, 'end': None})  # Stocăm intervalul curent
])

@app.callback(
    Output('stock-graph', 'figure'),
    Output('markers-state', 'data'),
    Output('current-range', 'data'),
    Input('search-button', 'n_clicks'),
    Input('stock-symbol', 'value'),
    Input('button-5d', 'n_clicks'),
    Input('button-1m', 'n_clicks'),
    Input('button-3m', 'n_clicks'),
    Input('button-6m', 'n_clicks'),
    Input('button-1y', 'n_clicks'),
    Input('button-5y', 'n_clicks'),
    Input('button-all', 'n_clicks'),
    Input('button-markers', 'n_clicks'),
    Input('current-range', 'data'),
    prevent_initial_call=True
)
def update_graph(n_clicks_search, symbol, n_clicks_5d, n_clicks_1m, n_clicks_3m, n_clicks_6m, n_clicks_1y, n_clicks_5y, n_clicks_all, n_clicks_markers, current_range):
    markers_state = True  # Valoare implicită
    try:
        if not symbol:
            symbol = 'AAPL'
        
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

        # Determinăm dacă markerii sunt activi sau nu
        show_markers = ctx.triggered and 'button-markers' in ctx.triggered[0]['prop_id']
        mode = 'lines+markers' if show_markers else 'lines'

        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Close'],
            mode=mode,  # Utilizează starea markerilor
            name=f'{symbol} - Preț de Închidere',
            marker=dict(size=8),
            text=[f"Date: {date}<br>Close: {close:.2f}<br>Open: {open:.2f}<br>High: {high:.2f}<br>Low: {low:.2f}<br>Volume: {volume}<br>Symbol: {symbol}" 
                  for date, close, open, high, low, volume in zip(df['Date'], df['Close'], df['Open'], df['High'], df['Low'], df['Volume'])],
            hoverinfo='text'
        ))

        # Setăm intervalul de timp pe baza butoanelor apăsate
        if ctx.triggered:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if button_id in ['button-5d', 'button-1m', 'button-3m', 'button-6m', 'button-1y', 'button-5y', 'button-all']:
                if button_id == 'button-5d':
                    new_range = {'start': df['Date'].max() - timedelta(days=5), 'end': df['Date'].max()}
                elif button_id == 'button-1m':
                    new_range = {'start': df['Date'].max() - timedelta(days=30), 'end': df['Date'].max()}
                elif button_id == 'button-3m':
                    new_range = {'start': df['Date'].max() - timedelta(days=93), 'end': df['Date'].max()}
                elif button_id == 'button-6m':
                    new_range = {'start': df['Date'].max() - timedelta(days=182), 'end': df['Date'].max()}
                elif button_id == 'button-1y':
                    new_range = {'start': df['Date'].max() - timedelta(days=365), 'end': df['Date'].max()}
                elif button_id == 'button-5y':
                    new_range = {'start': df['Date'].max() - timedelta(days=1825), 'end': df['Date'].max()}
                elif button_id == 'button-all':
                    new_range = {'start': df['Date'].min(), 'end': df['Date'].max()}
                
                # Actualizează graficul cu intervalul de timp selectat
                fig.update_xaxes(range=[new_range['start'], new_range['end']])
                
                # Salvează intervalul curent
                current_range = new_range

        else:
            # Dacă nu este niciun buton apăsat, utilizează intervalul de timp curent
            if current_range and current_range['start'] and current_range['end']:
                fig.update_xaxes(range=[current_range['start'], current_range['end']])
            else:
                # Dacă intervalul curent nu este definit, setăm intervalul complet al datelor
                fig.update_xaxes(range=[df['Date'].min(), df['Date'].max()])

        fig.update_layout(
            title=f'Price evolution for {company_name} ({symbol})<br>Last Close: {last_close_price_str} on {last_close_date_str}',
            title_x=0.5,  # Centrează titlul
            xaxis=dict(tickformat='%Y-%m-%d'),
            margin=dict(l=10, r=10, t=100, b=40)  # Ajustează marginile pentru a oferi spațiu pentru titlu
        )

    except Exception as e:
        # Dacă există o eroare, arată un grafic gol cu mesajul de eroare
        fig = go.Figure()
        fig.update_layout(
            title=f'Error: {str(e)}',
            xaxis=dict(tickformat='%Y-%m-%d'),
            margin=dict(l=10, r=10, t=100, b=40)  # Ajustează marginile pentru a oferi spațiu pentru titlu
        )
        markers_state = True  # Resetăm starea markerilor în caz de eroare
        # Asigurăm că intervalul este definit
        current_range = {'start': start_date.date(), 'end': end_date.date()}

    return fig, markers_state, current_range

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=10000, debug=True)

