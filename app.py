import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from datetime import datetime, timedelta
from dash import Dash, dcc, html, Input, Output, State, ctx

# Define the current date and start date
end_date = datetime.now()
start_date = end_date - timedelta(days=36500)  # Last 100 years to cover all periods

# Create the Dash app
app = Dash(__name__)

# Layout of the app
app.layout = html.Div([
    html.H1('Stock Price Evolution', style={'textAlign': 'center', 'marginBottom': '20px'}),

    # Text box for stock symbol and search button
    html.Div([
        dcc.Input(id='stock-symbol', type='text', value='AAPL', style={'marginRight': '10px', 'width': '60%'}),
        html.Button('Search Stock', id='search-button', n_clicks=0, style={'width': '30%'})
    ], className='input-container', style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'marginBottom': '10px'}),

    # Filtering buttons
    html.Div([
        html.Button('5D', id='button-5d', n_clicks=0),
        html.Button('1M', id='button-1m', n_clicks=0),
        html.Button('3M', id='button-3m', n_clicks=0),
        html.Button('6M', id='button-6m', n_clicks=0),
        html.Button('1Y', id='button-1y', n_clicks=0),
        html.Button('5Y', id='button-5y', n_clicks=0),
        html.Button('All', id='button-all', n_clicks=0),
    ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'center', 'marginBottom': '20px'}),

    # The graph will be updated here
    dcc.Graph(
        id='stock-graph',
        config={
            'displayModeBar': False,  # Disable mode bar
            'displaylogo': False,     # Disable Plotly logo
            'editable': False,        # Disable editing options
            'scrollZoom': False,      # Disable scroll zoom
            'showTips': False,        # Disable tooltips
            'showAxisDragHandles': False,  # Disable axis drag handles
            'modeBarButtonsToRemove': ['zoom', 'pan', 'resetScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian', 'toImage', 'sendDataToCloud']
        },
        style={'width': '100%', 'height': '70vh'}  # Adjust height for better fit
    ),

    # Storing the current range and current symbol
    dcc.Store(id='current-range', data={'start': None, 'end': None}),  # Store current range
    dcc.Store(id='current-symbol', data='AAPL'),  # Store current symbol
    dcc.Store(id='initial-load', data=True)  # Indicate initial load
])

@app.callback(
    [Output('stock-graph', 'figure'),
     Output('current-range', 'data'),
     Output('current-symbol', 'data'),
     Output('initial-load', 'data')],
    [Input('search-button', 'n_clicks'),
     Input('stock-symbol', 'n_submit'),
     Input('button-5d', 'n_clicks'),
     Input('button-1m', 'n_clicks'),
     Input('button-3m', 'n_clicks'),
     Input('button-6m', 'n_clicks'),
     Input('button-1y', 'n_clicks'),
     Input('button-5y', 'n_clicks'),
     Input('button-all', 'n_clicks'),
     Input('initial-load', 'data')],
    [State('stock-symbol', 'value'),
     State('current-range', 'data'),
     State('current-symbol', 'data')]
)
def update_graph(n_clicks_search, n_submit, n_clicks_5d, n_clicks_1m, n_clicks_3m, n_clicks_6m, n_clicks_1y, n_clicks_5y, n_clicks_all, initial_load, symbol_input, current_range, current_symbol):
    triggered_id = ctx.triggered_id
    symbol = symbol_input.upper() if triggered_id in ['search-button', 'stock-symbol'] else current_symbol
    
    # If the symbol has changed, reset the range
    if symbol != current_symbol:
        current_range = {'start': None, 'end': None}

    # Determine the time range based on button presses
    if triggered_id and triggered_id.startswith('button'):
        button_id = triggered_id
        if button_id == 'button-5d':
            new_range = {'start': datetime.now().date() - timedelta(days=5), 'end': datetime.now().date()}
        elif button_id == 'button-1m':
            new_range = {'start': datetime.now().date() - timedelta(days=30), 'end': datetime.now().date()}
        elif button_id == 'button-3m':
            new_range = {'start': datetime.now().date() - timedelta(days=93), 'end': datetime.now().date()}
        elif button_id == 'button-6m':
            new_range = {'start': datetime.now().date() - timedelta(days=182), 'end': datetime.now().date()}
        elif button_id == 'button-1y':
            new_range = {'start': datetime.now().date() - timedelta(days=365), 'end': datetime.now().date()}
        elif button_id == 'button-5y':
            new_range = {'start': datetime.now().date() - timedelta(days=1825), 'end': datetime.now().date()}
        elif button_id == 'button-all':
            new_range = {'start': start_date.date(), 'end': end_date.date()}

        current_range = new_range

    # Download data for the stock symbol
    try:
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

        # Get company info
        ticker = yf.Ticker(symbol)
        stock_info = ticker.info
        company_name = stock_info.get('longName', stock_info.get('shortName', symbol)) 

        last_close_price = df['Close'].iloc[-1] if not df['Close'].empty else 'N/A'
        last_close_date = df['Date'].iloc[-1] if not df['Date'].empty else 'N/A'

        last_close_price_str = f"{last_close_price:.2f}" if isinstance(last_close_price, (int, float)) else last_close_price
        last_close_date_str = last_close_date.strftime('%Y-%m-%d') if isinstance(last_close_date, datetime) else last_close_date

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Close'],
            mode='lines',
            name=f'{symbol} - Closing Price',
            text=[f"Date: {date}<br>Close: {close:.2f}<br>Open: {open:.2f}<br>High: {high:.2f}<br>Low: {low:.2f}<br>Volume: {volume}<br>Symbol: {symbol}" 
                  for date, close, open, high, low, volume in zip(df['Date'], df['Close'], df['Open'], df['High'], df['Low'], df['Volume'])],
            hoverinfo='text'
        ))

        if current_range['start'] and current_range['end']:
            fig.update_xaxes(range=[current_range['start'], current_range['end']])
        else:
            # Set initial range
            current_range = {'start': df['Date'].min(), 'end': df['Date'].max()}
            fig.update_xaxes(range=[current_range['start'], current_range['end']])

        fig.update_layout(
            title=f'Price Evolution for {company_name} ({symbol})<br>Last Close: {last_close_price_str} on {last_close_date_str}',
            title_x=0.5,
            xaxis=dict(tickformat='%Y-%m-%d'),
            margin=dict(l=10, r=10, t=100, b=40)
        )

    except Exception as e:
        fig = go.Figure()
        fig.update_layout(
            title=f'Error: {str(e)}',
            xaxis=dict(tickformat='%Y-%m-%d'),
            margin=dict(l=10, r=10, t=100, b=40)
        )
        current_range = {'start': start_date.date(), 'end': end_date.date()}
        current_symbol = 'AAPL'

    return fig, current_range, symbol, initial_load

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=10000, debug=False)

