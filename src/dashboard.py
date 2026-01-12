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

# Simple layout: symbol/provider/strategy selection, metrics, and charts
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("StrategyTester Dashboard", className="display-4 text-center mb-4"), width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Symbol", className="form-label fw-bold"),
                            dcc.Input(id='symbol', value='GOOGL', type='text', className="form-control mb-2")
                        ], md=2),
                        dbc.Col([
                            html.Label("Provider", className="form-label fw-bold"),
                            dcc.Dropdown(id='provider', options=[
                                {'label': 'Massive', 'value': 'massive'},
                                {'label': 'yFinance', 'value': 'yfinance'}
                            ], value='massive', className="mb-2")
                        ], md=2),
                        dbc.Col([
                            html.Label("Strategy", className="form-label fw-bold"),
                            dcc.Dropdown(id='strategy', options=[
                                {'label': 'SMA Crossover', 'value': 'sma_crossover'},
                                {'label': 'RSI Mean Reversion', 'value': 'rsi_mean_reversion'},
                                {'label': 'MACD Crossover', 'value': 'macd_crossover'}
                            ], value='sma_crossover', className="mb-2")
                        ], md=2),
                        dbc.Col([
                            html.Label("Fast (SMA/RSI)", className="form-label fw-bold"),
                            dcc.Input(id='fast', value=10, type='number', min=1, step=1, className="form-control mb-2")
                        ], md=2),
                        dbc.Col([
                            html.Label("Slow (SMA)", className="form-label fw-bold"),
                            dcc.Input(id='slow', value=50, type='number', min=1, step=1, className="form-control mb-2")
                        ], md=2),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Starting Capital", className="form-label fw-bold"),
                            dcc.Input(id='starting-capital', value=100000, type='number', min=1000, step=1000, className="form-control mb-2")
                        ], md=2),
                        dbc.Col([
                            html.Label("Risk Factor", className="form-label fw-bold"),
                            dcc.Input(id='risk-factor', value=1.0, type='number', min=0.01, max=10, step=0.01, className="form-control mb-2")
                        ], md=2),
                        dbc.Col([
                            html.Label("Slippage (%)", className="form-label fw-bold"),
                            dcc.Input(id='slippage', value=0.0, type='number', min=0, max=10, step=0.01, className="form-control mb-2")
                        ], md=2),
                        dbc.Col([
                            html.Label("Commission ($)", className="form-label fw-bold"),
                            dcc.Input(id='commission', value=0.0, type='number', min=0, max=100, step=0.01, className="form-control mb-2")
                        ], md=2),
                        dbc.Col([
                            dbc.Button('Run Backtest', id='run-btn', color='primary', className="me-2 mt-4"),
                            dbc.Button('Download Trades CSV', id='download-btn', color='secondary', className="mt-4")
                        ], md=2)
                    ])
                ])
            ], className="mb-4 shadow-sm")
        ], width=12)
    ]),
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
        State('starting-capital', 'value'), State('risk-factor', 'value'), State('slippage', 'value'), State('commission', 'value')
    ]
)
def update_dashboard(n_clicks, chart_toggles, selected_trade, symbol, provider, strategy, fast, slow, starting_capital, risk_factor, slippage, commission):
    if n_clicks == 0:
        return '', go.Figure(), go.Figure(), '', [], None, go.Figure()
    fetcher = DataFetcher()
    data = fetcher.cache.load(symbol, provider, 'parquet')
    if data is None:
        return f"No cached data for {symbol}/{provider}.", go.Figure(), go.Figure(), '', [], None, go.Figure()
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
    if 'equity' in chart_toggles:
        eq_fig.add_trace(go.Scatter(x=backtester.data.index, y=backtester.data['equity'], mode='lines', name='Equity'))
        eq_fig.update_layout(title='Equity Curve', xaxis_title='Date', yaxis_title='Equity')
    # Price + signals
    price_fig = go.Figure()
    if 'price' in chart_toggles:
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
    data = fetcher.cache.load(symbol, provider, 'parquet')
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

if __name__ == '__main__':
    app.run(debug=True)
