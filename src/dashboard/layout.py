# Main layout definition for dashboard

import dash_bootstrap_components as dbc
from dash import dcc, html
from .components.glossary_search import glossary_search_component

symbol_list = sorted(list(set([
	'AAPL', 'AMZN', 'BA', 'BAC', 'GOOGL', 'JNJ', 'JPM', 'MSFT', 'SPY', 'TSLA', 'UNH', 'UNP'
])))

layout = dbc.Container([
    html.Script(src="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.js"),
	dbc.Row([
		dbc.Col([
			html.Div([
				html.H1("StrategyTester Dashboard", className="display-4 mb-4", style={"display": "inline-block", "verticalAlign": "middle"}),
				glossary_search_component()
			], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"})
		], width=12)
	]),
		   dbc.Row([
			   dbc.Col([
				   dbc.Card([
					   dbc.CardHeader(html.H5("Data Selection")),
					   dbc.CardBody([
						   dbc.Row([
							   dbc.Col([
								   html.Label(["Symbol ", html.I(className="bi bi-info-circle", id="tt-symbol")], className="form-label fw-bold data-selection-label"),
								   dcc.Dropdown(
									   id='symbol',
									   options=[{'label': s, 'value': s} for s in symbol_list],
									   value=symbol_list[0],
									   className="mb-2 data-selection-dropdown"
								   )
							   ], md=2),
							   dbc.Col([
								   html.Label(["Provider ", html.I(className="bi bi-info-circle", id="tt-provider")], className="form-label fw-bold data-selection-label"),
								   dcc.Dropdown(id='provider', options=[
									   {'label': 'Auto', 'value': 'auto'},
									   {'label': 'Massive', 'value': 'massive'},
									   {'label': 'yFinance', 'value': 'yfinance'}
								   ], value='auto', className="mb-2 data-selection-dropdown")
							   ], md=2),
							   dbc.Col([
								   html.Label(["Timeframe ", html.I(className="bi bi-info-circle", id="tt-timeframe")], className="form-label fw-bold data-selection-label"),
								   dcc.Dropdown(id='timeframe', options=[
									   {'label': 'Daily', 'value': '1d'},
									   {'label': '1 Minute', 'value': '1min'},
									   {'label': '5 Minute', 'value': '5min'},
									   {'label': '1 Hour', 'value': '1h'}
								   ], value='1d', className="mb-2 data-selection-dropdown")
							   ], md=2),
							   dbc.Col([
								   html.Label(["Start Date ", html.I(className="bi bi-info-circle", id="tt-start-date")], className="form-label fw-bold data-selection-label"),
								   dcc.DatePickerSingle(id='start-date', date=None, className="mb-2 data-selection-dropdown")
							   ], md=2),
							   dbc.Col([
								   html.Label(["End Date ", html.I(className="bi bi-info-circle", id="tt-end-date")], className="form-label fw-bold data-selection-label"),
								   dcc.DatePickerSingle(id='end-date', date=None, className="mb-2 data-selection-dropdown")
							   ], md=2),
						   ], className="data-selection-row"),
						   dbc.Row([
							   dbc.Col([
								   html.Label(["Cached Data Set ", html.I(className="bi bi-info-circle", id="tt-cache-file")], className="form-label fw-bold data-selection-label"),
								   dcc.Dropdown(id='cache-file-dropdown', options=[], value=None, clearable=True, className="mb-2 data-selection-dropdown")
							   ], md=4)
						   ], className="data-selection-row")
					   ])
				   ], className="mb-3 shadow-sm data-selection-card h-100"),
			   ], width=4),
			   dbc.Col([
				   dbc.Card([
					   dbc.CardHeader(html.H5("Strategy Parameters")),
					   dbc.CardBody([
						   dbc.Row([
							   dbc.Col([
								   html.Label(["Strategy ", html.I(className="bi bi-info-circle", id="tt-strategy")], className="form-label fw-bold data-selection-label"),
								   dcc.Dropdown(id='strategy', options=[
									   {'label': 'SMA Crossover', 'value': 'sma_crossover'},
									   {'label': 'RSI Mean Reversion', 'value': 'rsi_mean_reversion'},
									   {'label': 'MACD Crossover', 'value': 'macd_crossover'},
									   {'label': 'Impulse MACD', 'value': 'impulse_macd'}
								   ], value='sma_crossover', className="mb-2 data-selection-dropdown")
							   ], md=12),
							   dbc.Col([
								   html.Label(["Fast (SMA/RSI) ", html.I(className="bi bi-info-circle", id="tt-fast")], className="form-label fw-bold data-selection-label"),
								   dcc.Input(id='fast', value=10, type='number', min=1, step=1, className="form-control mb-2")
							   ], md=6),
							   dbc.Col([
								   html.Label(["Slow (SMA) ", html.I(className="bi bi-info-circle", id="tt-slow")], className="form-label fw-bold data-selection-label"),
								   dcc.Input(id='slow', value=50, type='number', min=1, step=1, className="form-control mb-2")
							   ], md=6),
						   ])
					   ])
				   ], className="mb-3 shadow-sm data-selection-card h-100"),
			   ], width=4),
			   dbc.Col([
				   dbc.Card([
					   dbc.CardHeader(html.H5("Backtest Settings")),
					   dbc.CardBody([
						   dbc.Row([
							   dbc.Col([
								   html.Label(["Starting Capital ", html.I(className="bi bi-info-circle", id="tt-starting-capital")], className="form-label fw-bold data-selection-label"),
								   dcc.Input(id='starting-capital', value=100000, type='number', min=1000, step=1000, className="form-control mb-2")
							   ], md=12),
							   dbc.Col([
								   html.Label(["Risk Factor ", html.I(className="bi bi-info-circle", id="tt-risk-factor")], className="form-label fw-bold data-selection-label"),
								   dcc.Input(id='risk-factor', value=1.0, type='number', min=0.01, max=10, step=0.01, className="form-control mb-2")
							   ], md=6),
							   dbc.Col([
								   html.Label(["Risk:Reward ", html.I(className="bi bi-info-circle", id="tt-risk-reward")], className="form-label fw-bold data-selection-label"),
								   dcc.Input(id='risk-reward', value=3.0, type='number', min=0.5, max=10, step=0.1, className="form-control mb-2")
							   ], md=6),
							   dbc.Col([
								   html.Label(["Slippage (%) ", html.I(className="bi bi-info-circle", id="tt-slippage")], className="form-label fw-bold data-selection-label"),
								   dcc.Input(id='slippage', value=0.0, type='number', min=0, max=10, step=0.01, className="form-control mb-2")
							   ], md=6),
							   dbc.Col([
								   html.Label(["Commission ($) ", html.I(className="bi bi-info-circle", id="tt-commission")], className="form-label fw-bold data-selection-label"),
								   dcc.Input(id='commission', value=0.0, type='number', min=0, max=100, step=0.01, className="form-control mb-2")
							   ], md=6),
							   dbc.Col([
								   dbc.Button('Run Backtest', id='run-btn', color='primary', className="me-2 mt-4"),
								   dbc.Button('Download Trades CSV', id='download-btn', color='secondary', className="mt-4")
							   ], md=12)
						   ])
					   ])
				   ], className="mb-3 shadow-sm data-selection-card h-100"),
			   ], width=4),
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
		], width=8),
		dbc.Col([
			dbc.Card([
				dbc.CardBody([
					html.H4("Win/Loss Pie", className="card-title mb-3"),
					dcc.Graph(id='win-loss-pie')
				])
			], className="mb-4 shadow-sm"),
		], width=4),
	]),
	dbc.Row([
		dbc.Col([
			dbc.Card([
				dbc.CardBody([
					html.H4("Biggest Winner Trade", className="card-title mb-3"),
					dcc.Graph(id='biggest-winner-chart')
				])
			], className="mb-4 shadow-sm"),
		], width=6),
		dbc.Col([
			dbc.Card([
				dbc.CardBody([
					html.H4("Biggest Loser Trade", className="card-title mb-3"),
					dcc.Graph(id='biggest-loser-chart')
				])
			], className="mb-4 shadow-sm"),
		], width=6),
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
# Main layout definition for dashboard
