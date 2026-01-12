
"""
Dash/Plotly dashboard for visualizing backtest results and strategy performance.
Run with: python src/dashboard.py
"""


import dash
from dash import dcc, html, Input, Output, State, no_update
import plotly.graph_objs as go
import pandas as pd
import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_fetchers import DataFetcher
from src.strategies.sma_crossover import SmaCrossoverStrategy
from src.strategies.rsi_mean_reversion import RsiMeanReversionStrategy
from src.strategies.macd_crossover import MACDCrossoverStrategy
from src.backtester import Backtester


# Use a modern external stylesheet (Dash Bootstrap)
import dash_bootstrap_components as dbc
import os

# Explicitly set the assets folder to the project root assets directory
assets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    assets_folder=assets_path
)

# Add this after app = dash.Dash(...) and before app.layout = ...
from dash.dependencies import Input, Output

# Populate cache-file-dropdown options based on symbol, provider, and timeframe
@app.callback(
    Output('cache-file-dropdown', 'options'),
    [Input('symbol', 'value'), Input('provider', 'value'), Input('timeframe', 'value')]
)
def update_cache_file_options(symbol, provider, timeframe):
    import os
    # If any required value is None, return empty options
    if not symbol or not provider or not timeframe:
        return []
    # Map timeframe for cache folder
    tf_map = {'1d': 'day', '1min': 'minute', '1m': 'minute', '5min': 'minute', '1h': 'hour'}
    def get_cache_timeframe(provider, timeframe):
        if provider == 'massive':
            return tf_map.get(timeframe, timeframe)
        return timeframe
    chosen_provider = provider
    if provider == 'auto':
        chosen_provider = 'massive'  # fallback for dropdown population
    cache_timeframe = get_cache_timeframe(chosen_provider, timeframe)
    # Ensure all path components are strings
    cache_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cache', str(chosen_provider), str(symbol), str(cache_timeframe)))
    options = []
    if os.path.isdir(cache_dir):
        files = [f for f in os.listdir(cache_dir) if f.endswith('.parquet')]
        options = [{'label': f, 'value': f} for f in sorted(files)]
    return options

# Simple layout: symbol/provider/strategy selection, metrics, and charts
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("StrategyTester Dashboard", className="display-4 text-center mb-4"), width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Data Selection")),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label(["Symbol ", html.I(className="bi bi-info-circle", id="tt-symbol")], className="form-label fw-bold"),
                            dcc.Dropdown(
                                id='symbol',
                                options=[
                                    {'label': s, 'value': s} for s in sorted(list(set([
                                        'AAPL', 'AMZN', 'BA', 'BAC', 'GOOGL', 'JNJ', 'JPM', 'MSFT', 'SPY', 'TSLA', 'UNH', 'UNP'
                                    ])))
                                ],
                                value='SPY',
                                className="mb-2"
                            )
                        ], md=2),
                        dbc.Col([
                            html.Label(["Provider ", html.I(className="bi bi-info-circle", id="tt-provider")], className="form-label fw-bold"),
                            dcc.Dropdown(id='provider', options=[
                                {'label': 'Auto', 'value': 'auto'},
                                {'label': 'Massive', 'value': 'massive'},
                                {'label': 'yFinance', 'value': 'yfinance'}
                            ], value='auto', className="mb-2")
                        ], md=2),
                        dbc.Col([
                            html.Label(["Timeframe ", html.I(className="bi bi-info-circle", id="tt-timeframe")], className="form-label fw-bold"),
                            dcc.Dropdown(id='timeframe', options=[
                                {'label': 'Daily', 'value': '1d'},
                                {'label': '1 Minute', 'value': '1min'},
                                {'label': '5 Minute', 'value': '5min'},
                                {'label': '1 Hour', 'value': '1h'}
                            ], value='1d', className="mb-2")
                        ], md=2),
                        dbc.Col([
                            html.Label(["Start Date ", html.I(className="bi bi-info-circle", id="tt-start-date")], className="form-label fw-bold"),
                            dcc.DatePickerSingle(id='start-date', date=None, className="mb-2")
                        ], md=2),
                        dbc.Col([
                            html.Label(["End Date ", html.I(className="bi bi-info-circle", id="tt-end-date")], className="form-label fw-bold"),
                            dcc.DatePickerSingle(id='end-date', date=None, className="mb-2")
                        ], md=2),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.Label(["Cached Data Set ", html.I(className="bi bi-info-circle", id="tt-cache-file")], className="form-label fw-bold"),
                            dcc.Dropdown(id='cache-file-dropdown', options=[], value=None, clearable=True, className="mb-2")
                        ], md=4)
                    ])
                ])
            ], className="mb-3 shadow-sm"),
            dbc.Card([
                dbc.CardHeader(html.H5("Strategy Parameters")),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label(["Strategy ", html.I(className="bi bi-info-circle", id="tt-strategy")], className="form-label fw-bold"),
                            dcc.Dropdown(id='strategy', options=[
                                {'label': 'SMA Crossover', 'value': 'sma_crossover'},
                                {'label': 'RSI Mean Reversion', 'value': 'rsi_mean_reversion'},
                                {'label': 'MACD Crossover', 'value': 'macd_crossover'}
                            ], value='sma_crossover', className="mb-2")
                        ], md=3),
                        dbc.Col([
                            html.Label(["Fast (SMA/RSI) ", html.I(className="bi bi-info-circle", id="tt-fast")], className="form-label fw-bold"),
                            dcc.Input(id='fast', value=10, type='number', min=1, step=1, className="form-control mb-2")
                        ], md=3),
                        dbc.Col([
                            html.Label(["Slow (SMA) ", html.I(className="bi bi-info-circle", id="tt-slow")], className="form-label fw-bold"),
                            dcc.Input(id='slow', value=50, type='number', min=1, step=1, className="form-control mb-2")
                        ], md=3),
                    ])
                ])
            ], className="mb-3 shadow-sm"),
            dbc.Card([
                dbc.CardHeader(html.H5("Backtest Settings")),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label(["Starting Capital ", html.I(className="bi bi-info-circle", id="tt-starting-capital")], className="form-label fw-bold"),
                            dcc.Input(id='starting-capital', value=100000, type='number', min=1000, step=1000, className="form-control mb-2")
                        ], md=3),
                        dbc.Col([
                            html.Label(["Risk Factor ", html.I(className="bi bi-info-circle", id="tt-risk-factor")], className="form-label fw-bold"),
                            dcc.Input(id='risk-factor', value=1.0, type='number', min=0.01, max=10, step=0.01, className="form-control mb-2")
                        ], md=3),
                        dbc.Col([
                            html.Label(["Slippage (%) ", html.I(className="bi bi-info-circle", id="tt-slippage")], className="form-label fw-bold"),
                            dcc.Input(id='slippage', value=0.0, type='number', min=0, max=10, step=0.01, className="form-control mb-2")
                        ], md=3),
                        dbc.Col([
                            html.Label(["Commission ($) ", html.I(className="bi bi-info-circle", id="tt-commission")], className="form-label fw-bold"),
                            dcc.Input(id='commission', value=0.0, type='number', min=0, max=100, step=0.01, className="form-control mb-2")
                        ], md=3),
                        dbc.Col([
                            dbc.Button('Run Backtest', id='run-btn', color='primary', className="me-2 mt-4"),
                            dbc.Button('Download Trades CSV', id='download-btn', color='secondary', className="mt-4")
                        ], md=3)
                    ])
                ])
            ], className="mb-4 shadow-sm")
        ], width=12)
    ]),
        # Tooltips for each parameter
        dbc.Tooltip("Stock ticker symbol (e.g., AAPL, MSFT, SPY)", target="tt-symbol", placement="top"),
        dbc.Tooltip("Data provider: Massive (Polygon) or yFinance", target="tt-provider", placement="top"),
        dbc.Tooltip("Data timeframe: daily, 1min, 5min, or 1h", target="tt-timeframe", placement="top"),
        dbc.Tooltip("Start date for data selection", target="tt-start-date", placement="top"),
        dbc.Tooltip("End date for data selection", target="tt-end-date", placement="top"),
        dbc.Tooltip("Strategy to use for backtesting", target="tt-strategy", placement="top"),
        dbc.Tooltip("Fast parameter for SMA/RSI/MACD (short window)", target="tt-fast", placement="top"),
        dbc.Tooltip("Slow parameter for SMA/MACD (long window)", target="tt-slow", placement="top"),
        dbc.Tooltip("Initial capital for backtest", target="tt-starting-capital", placement="top"),
        dbc.Tooltip("Risk factor for position sizing (future use)", target="tt-risk-factor", placement="top"),
        dbc.Tooltip("Slippage percentage per trade (future use)", target="tt-slippage", placement="top"),
        dbc.Tooltip("Commission per trade in dollars", target="tt-commission", placement="top"),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Performance Metrics", className="card-title mb-3"),
                    html.Div(id='metrics', className="mb-2")
                ])
            ], className="mb-4 shadow-sm")
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Checklist(
                        id='chart-toggles',
                        options=[
                            {'label': 'Show Equity Curve', 'value': 'equity'},
                            {'label': 'Show Price & Signals', 'value': 'price'}
                        ],
                        value=['equity', 'price'],
                        inline=True,
                        className="mb-3"
                    ),
                    dcc.Graph(id='equity-curve', className="mb-4"),
                    dcc.Graph(id='price-signals')
                ])
            ], className="mb-4 shadow-sm")
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Trade List", className="card-title mb-3"),
                    html.Div(id='trade-table'),
                    html.Br(),
                    html.Label("Select Trade to View Candlestick Chart:"),
                    dcc.Dropdown(id='trade-selector', options=[], value=None, clearable=True, style={"maxWidth": 400}),
                    dcc.Graph(id='trade-candlestick')
                ])
            ], className="mb-4 shadow-sm")
        ], width=12)
    ]),
    dcc.Download(id="download-trades")
], fluid=True)




def compute_extra_metrics(backtester, results):
    # Add more detailed metrics
    equity = backtester.data['equity']
    returns = backtester.data['strategy_returns']
    n_years = (equity.index[-1] - equity.index[0]).days / 365.25
    cagr = (equity.iloc[-1] / equity.iloc[0]) ** (1 / n_years) - 1 if n_years > 0 else np.nan
    win_trades = backtester.data['strategy_returns'][backtester.data['strategy_returns'] > 0].count()
    loss_trades = backtester.data['strategy_returns'][backtester.data['strategy_returns'] < 0].count()
    win_rate = win_trades / (win_trades + loss_trades) if (win_trades + loss_trades) > 0 else np.nan
    avg_trade = returns.mean()
    results['CAGR'] = cagr
    results['win_rate'] = win_rate
    results['avg_trade'] = avg_trade
    return results

def trades_to_table(trades, backtester):
    if trades.empty:
        return html.Div("No trades.")
    rows = []
    for _, t in trades.iterrows():
        entry = t['entry']
        exit = t['exit']
        side = t['side']
        entry_price = backtester.data.loc[entry, 'close'] if entry in backtester.data.index else None
        exit_price = backtester.data.loc[exit, 'close'] if exit in backtester.data.index else None
        pnl = (exit_price - entry_price) * side if entry_price and exit_price else None
        duration = (exit - entry).days if hasattr(exit, 'days') else ''
        rows.append(html.Tr([
            html.Td(str(entry)),
            html.Td(str(exit)),
            html.Td('Long' if side == 1 else 'Short'),
            html.Td(f"{entry_price:.2f}" if entry_price else ''),
            html.Td(f"{exit_price:.2f}" if exit_price else ''),
            html.Td(f"{pnl:.2f}" if pnl else ''),
            html.Td(str(duration))
        ]))
    return html.Table([
        html.Thead(html.Tr([html.Th(h) for h in ['Entry', 'Exit', 'Side', 'Entry Price', 'Exit Price', 'PnL', 'Duration']])),
        html.Tbody(rows)
    ], style={'width': '100%', 'border': '1px solid #ccc'})


# Store trades and backtester in a global cache for callbacks
from dash import ctx
import dash
global_cache = {}

@app.callback(
    [Output('metrics', 'children'), Output('equity-curve', 'figure'), Output('price-signals', 'figure'), Output('trade-table', 'children'), Output('trade-selector', 'options'), Output('trade-selector', 'value'), Output('trade-candlestick', 'figure')],
    [Input('run-btn', 'n_clicks'), Input('chart-toggles', 'value'), Input('trade-selector', 'value')],
    [
        State('symbol', 'value'), State('provider', 'value'), State('strategy', 'value'),
        State('fast', 'value'), State('slow', 'value'),
        State('starting-capital', 'value'), State('risk-factor', 'value'), State('slippage', 'value'), State('commission', 'value'),
        State('cache-file-dropdown', 'value')
    ]
)
def update_dashboard(n_clicks, chart_toggles, selected_trade, symbol, provider, strategy, fast, slow, starting_capital, risk_factor, slippage, commission, selected_cache_file):
    if n_clicks == 0:
        return '', go.Figure(), go.Figure(), '', [], None, go.Figure()
    fetcher = DataFetcher()
    # Get timeframe and date range from UI
    ctx_inputs = dash.callback_context.inputs
    timeframe = ctx_inputs.get('timeframe.value', '1d') if hasattr(ctx_inputs, 'get') else '1d'
    start_date = ctx_inputs.get('start-date.date', None)
    end_date = ctx_inputs.get('end-date.date', None)
    date_range = f"{start_date}_to_{end_date}" if start_date and end_date else None

    # Timeframe mapping for cache folder
    tf_map = {'1d': 'day', '1min': 'minute', '1m': 'minute', '5min': 'minute', '1h': 'hour'}

    # Auto-pick provider logic
    chosen_provider = provider
    warning = ''
    # Always map timeframe for massive, even if date_range is None
    def get_cache_timeframe(provider, timeframe):
        if provider == 'massive':
            return tf_map.get(timeframe, timeframe)
        return timeframe

    cache_timeframe = get_cache_timeframe(provider, timeframe)
    if provider == 'auto':
        # If 1m timeframe and <=7 days, prefer yfinance, else massive
        if timeframe in ['1m', '1min', 'minute']:
            if start_date and end_date:
                from datetime import datetime
                d0 = datetime.strptime(start_date, '%Y-%m-%d')
                d1 = datetime.strptime(end_date, '%Y-%m-%d')
                days = (d1 - d0).days + 1
                if days <= 7:
                    chosen_provider = 'yfinance'
                else:
                    chosen_provider = 'massive'
            else:
                chosen_provider = 'yfinance'  # fallback
        else:
            chosen_provider = 'massive'
        cache_timeframe = get_cache_timeframe(chosen_provider, timeframe)

    # Use selected cache file if provided
    if selected_cache_file:
        cache_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cache', str(chosen_provider), str(symbol), str(cache_timeframe), selected_cache_file))
        if os.path.exists(cache_path):
            data = pd.read_parquet(cache_path)
            date_range = os.path.splitext(selected_cache_file)[0]
        else:
            data = None
    else:
        data = fetcher.cache.load(symbol, chosen_provider, cache_timeframe, 'parquet', date_range)
        warning = f"No cached data for {symbol}/{chosen_provider}/{cache_timeframe}/{date_range}."
        return warning, go.Figure(), go.Figure(), '', [], None, go.Figure()
    if data is None:
        warning = f"No data loaded for {symbol}/{chosen_provider}/{cache_timeframe}/{date_range}."
        return warning, go.Figure(), go.Figure(), '', [], None, go.Figure()

    if strategy == 'sma_crossover':
        strat = SmaCrossoverStrategy(fast=fast, slow=slow)
    elif strategy == 'rsi_mean_reversion':
        strat = RsiMeanReversionStrategy()
    elif strategy == 'macd_crossover':
        strat = MACDCrossoverStrategy(fast=fast, slow=slow)
    else:
        return f"Unknown strategy: {strategy}", go.Figure(), go.Figure(), '', [], None, go.Figure()
    # Only pass supported args to Backtester
    backtester = Backtester(data, strat, initial_cash=starting_capital, fee=commission)
    # risk_factor and slippage are available for future use
    results = backtester.run()
    results = compute_extra_metrics(backtester, results)
    # Metrics
    metrics = html.Ul([
        html.Li(f"Final Equity: {results['final_equity']:.2f}"),
        html.Li(f"Total Return: {results['total_return']:.2%}"),
        html.Li(f"Max Drawdown: {results['max_drawdown']:.2%}"),
        html.Li(f"Sharpe Ratio: {results['sharpe']:.2f}"),
        html.Li(f"CAGR: {results['CAGR']:.2%}"),
        html.Li(f"Win Rate: {results['win_rate']:.2%}"),
        html.Li(f"Avg Trade: {results['avg_trade']:.4f}"),
        html.Li(f"Number of Trades: {results['num_trades']}")
    ])
    # Equity curve
    eq_fig = go.Figure()
    # Price & signals figure
    price_fig = go.Figure()
    if 'equity' in chart_toggles:
        eq_fig.add_trace(go.Scatter(x=backtester.data.index, y=backtester.data['equity'], mode='lines', name='Equity'))
        eq_fig.update_layout(title='Equity Curve', xaxis_title='Date', yaxis_title='Equity')
    # Price + signals
        # Use selected cache file if provided
        ctx = dash.callback_context
        cache_file = None
        if ctx and ctx.states and 'cache-file-dropdown.value' in ctx.states:
            cache_file = ctx.states['cache-file-dropdown.value']
        if cache_file:
            cache_path = os.path.join(os.path.dirname(__file__), '..', 'cache', chosen_provider, symbol, cache_timeframe, cache_file)
            if os.path.exists(cache_path):
                data = pd.read_parquet(cache_path)
                date_range = os.path.splitext(cache_file)[0]
            else:
                data = None
        else:
            data = fetcher.cache.load(symbol, chosen_provider, cache_timeframe, 'parquet', date_range)
        price_fig.add_trace(go.Scatter(x=backtester.data.index, y=backtester.data['close'], mode='lines', name='Close'))
        buys = backtester.data[backtester.data['signal'] == 1]
        sells = backtester.data[backtester.data['signal'] == -1]
        price_fig.add_trace(go.Scatter(x=buys.index, y=buys['close'], mode='markers', marker_symbol='triangle-up', marker_color='green', marker_size=10, name='Buy'))
        price_fig.add_trace(go.Scatter(x=sells.index, y=sells['close'], mode='markers', marker_symbol='triangle-down', marker_color='red', marker_size=10, name='Sell'))
        price_fig.update_layout(title='Price & Signals', xaxis_title='Date', yaxis_title='Price')
    # Trade table
    trades = backtester._extract_trades()
    trade_table = trades_to_table(trades, backtester)
    # Trade selector options
    trade_options = [
        {'label': f"{idx+1}: {str(t['entry'])[:10]} → {str(t['exit'])[:10]} ({'Long' if t['side']==1 else 'Short'})", 'value': idx}
        for idx, (_, t) in enumerate(trades.iterrows())
    ]
    # Default to first trade if available
    trade_value = selected_trade if selected_trade is not None else (0 if len(trade_options) > 0 else None)
    # Candlestick chart for selected trade
    trade_fig = go.Figure()
    if trade_value is not None and len(trades) > 0:
        t = trades.iloc[trade_value]
        entry, exit = t['entry'], t['exit']
        df = backtester.data.loc[entry:exit]
        trade_fig = go.Figure(data=[
            go.Candlestick(
                x=df.index,
                open=df['open'], high=df['high'], low=df['low'], close=df['close'],
                name='Candles',
                increasing_line_color='green', decreasing_line_color='red',
            )
        ])
        # Entry marker
        trade_fig.add_trace(go.Scatter(x=[entry], y=[df.loc[entry, 'close']], mode='markers', marker=dict(color='blue', size=12, symbol='star'), name='Entry'))
        # Exit marker
        trade_fig.add_trace(go.Scatter(x=[exit], y=[df.loc[exit, 'close']], mode='markers', marker=dict(color='orange', size=12, symbol='x'), name='Exit'))
        # (Optional) SL/TP markers: if your strategy provides them, add here
        trade_fig.update_layout(title=f"Trade {trade_value+1}: {entry} → {exit}", xaxis_title='Date', yaxis_title='Price')
    return metrics, eq_fig, price_fig, trade_table, trade_options, trade_value, trade_fig

# Download trades as CSV
@app.callback(
    Output("download-trades", "data"),
    [Input("download-btn", "n_clicks")],
    [State('symbol', 'value'), State('provider', 'value'), State('strategy', 'value'), State('fast', 'value'), State('slow', 'value')]
)
def download_trades(n_clicks, symbol, provider, strategy, fast, slow):
    if n_clicks == 0:
        return no_update
    fetcher = DataFetcher()
    # For download, try to get timeframe and date range from State if available
    import dash
    ctx_inputs = dash.callback_context.states
    timeframe = ctx_inputs.get('timeframe.value', '1d') if hasattr(ctx_inputs, 'get') else '1d'
    start_date = ctx_inputs.get('start-date.date', None)
    end_date = ctx_inputs.get('end-date.date', None)
    date_range = f"{start_date}_to_{end_date}" if start_date and end_date else None
    # Timeframe mapping for cache folder
    tf_map = {'1d': 'day', '1min': 'minute', '1m': 'minute', '5min': 'minute', '1h': 'hour'}
    cache_timeframe = timeframe
    if provider == 'massive':
        cache_timeframe = tf_map.get(timeframe, timeframe)
    data = fetcher.cache.load(symbol, provider, cache_timeframe, 'parquet', date_range)
    if data is None:
        return no_update
    if strategy == 'sma_crossover':
        strat = SmaCrossoverStrategy(fast=fast, slow=slow)
    elif strategy == 'rsi_mean_reversion':
        strat = RsiMeanReversionStrategy()
    elif strategy == 'macd_crossover':
        strat = MACDCrossoverStrategy(fast=fast, slow=slow)
    else:
        return no_update
    backtester = Backtester(data, strat)
    backtester.run()  # Ensure 'position' and other columns are created
    trades = backtester._extract_trades()
    if trades.empty:
        return no_update
    csv_string = trades.to_csv(index=False)
    return {
        'content': csv_string,
        'filename': f"trades_{symbol}_{provider}.csv",
        'type': 'text/csv'
    }

from dash.dependencies import Input, Output, State
import glob
import re

# Helper to get earliest and latest date from cache

def get_date_range_from_cache(symbol, provider, timeframe):
    cache_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cache'))
    tf_map = {'1d': 'day', '1min': 'minute', '1m': 'minute', '5min': 'minute', '1h': 'hour'}
    tf_folder = tf_map.get(timeframe, timeframe)
    # Try both yfinance and massive if provider is 'auto'
    providers = [provider] if provider != 'auto' else ['yfinance', 'massive']
    all_dates = []
    for prov in providers:
        # Ensure all join arguments are str, not None
        if not (cache_root and prov and symbol and tf_folder):
            continue
        folder = os.path.join(str(cache_root), str(prov), str(symbol), str(tf_folder))
        if not os.path.isdir(folder):
            continue
        for f in glob.glob(os.path.join(folder, '*.parquet')):
            m = re.search(r'(\d{4}-\d{2}-\d{2})_to_(\d{4}-\d{2}-\d{2})', f)
            if m:
                all_dates.append((m.group(1), m.group(2)))
    if not all_dates:
        return None, None
    starts, ends = zip(*all_dates)
    return min(starts), max(ends)

@app.callback(
    [Output('start-date', 'date'), Output('end-date', 'date')],
    [Input('symbol', 'value'), Input('provider', 'value'), Input('timeframe', 'value')]
)
def update_date_range(symbol, provider, timeframe):
    start, end = get_date_range_from_cache(symbol, provider, timeframe)
    # If no data, clear the pickers
    if not start or not end:
        return None, None
    return start, end

if __name__ == '__main__':
    app.run(debug=True)
