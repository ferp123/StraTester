

from dash import Input, Output, State, no_update, callback_context
import plotly.graph_objs as go
import pandas as pd
import os
import numpy as np
from data_fetchers import DataFetcher
from strategies.sma_crossover import SmaCrossoverStrategy
from strategies.rsi_mean_reversion import RsiMeanReversionStrategy
from strategies.macd_crossover import MACDCrossoverStrategy
from strategies.impulse_macd import ImpulseMACDStrategy
from backtester import Backtester
from .utils import compute_extra_metrics, trades_to_table
from .components.metrics_panel import metrics_panel
from .components.trade_table import trade_table
from dash import html

def register_callbacks(app):
	# Populate cache-file-dropdown options based on symbol, provider, and timeframe
	@app.callback(
		[Output('cache-file-dropdown', 'options'), Output('cache-file-dropdown', 'value')],
		[Input('symbol', 'value'), Input('provider', 'value'), Input('timeframe', 'value')]
	)
	def update_cache_file_options(symbol, provider, timeframe):
		import os
		if not symbol or not provider or not timeframe:
			return [], None
		tf_map = {'1d': 'day', '1min': 'minute', '1m': 'minute', '5min': 'minute', '1h': 'hour'}
		def get_cache_timeframe(provider, timeframe):
			if provider in ['massive', 'auto']:
				return tf_map.get(timeframe, timeframe)
			return timeframe
		# Always use 'massive' for cache lookup if provider is 'auto' or 'massive'
		chosen_provider = 'massive' if provider in ['auto', 'massive'] else provider
		cache_timeframe = get_cache_timeframe(chosen_provider, timeframe)
		# Find project root (two levels up from this file)
		project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
		cache_dir = os.path.join(project_root, 'cache', str(chosen_provider), str(symbol), str(cache_timeframe))
		print(f"[DEBUG] Looking for cached data sets in: {cache_dir}")
		print(f"[DEBUG] Looking for cached data sets in: {cache_dir}")
		options = []
		value = None
		if os.path.isdir(cache_dir):
			files = [f for f in os.listdir(cache_dir) if f.endswith('.parquet')]
			print(f"[DEBUG] Found files: {files}")
			files = sorted(files)
			options = [{'label': f, 'value': f} for f in files]
			if files:
				value = files[0]
		else:
			print(f"[DEBUG] Directory does not exist: {cache_dir}")
		return options, value

	# Main dashboard update callback
	@app.callback(
		[
			Output('metrics', 'children'),
			Output('equity-curve', 'figure'),
			Output('price-signals', 'figure'),
			Output('trade-table', 'children'),
			Output('trade-selector', 'options'),
			Output('trade-selector', 'value'),
			Output('trade-candlestick', 'figure'),
			Output('biggest-winner-chart', 'figure'),
			Output('biggest-loser-chart', 'figure'),
			Output('win-loss-pie', 'figure'),
		],
		[Input('run-btn', 'n_clicks'), Input('chart-toggles', 'value'), Input('trade-selector', 'value')],
		[
			State('symbol', 'value'), State('provider', 'value'), State('strategy', 'value'),
			State('fast', 'value'), State('slow', 'value'),
			State('starting-capital', 'value'), State('risk-factor', 'value'), State('risk-reward', 'value'), State('slippage', 'value'), State('commission', 'value'),
			State('cache-file-dropdown', 'value')
		]
	)
	def update_dashboard(n_clicks, chart_toggles, selected_trade, symbol, provider, strategy, fast, slow, starting_capital, risk_factor, risk_reward, slippage, commission, selected_cache_file):
		ctx_inputs = callback_context.inputs if hasattr(callback_context, 'inputs') else {}
		timeframe = ctx_inputs.get('timeframe.value', '1d') if hasattr(ctx_inputs, 'get') else '1d'
		start_date = ctx_inputs.get('start-date.date', None)
		end_date = ctx_inputs.get('end-date.date', None)
		print(f"[DEBUG] Run Backtest Clicked: n_clicks={n_clicks}, symbol={symbol}, provider={provider}, timeframe={timeframe}, start_date={start_date}, end_date={end_date}, selected_cache_file={selected_cache_file}, strategy={strategy}, fast={fast}, slow={slow}, starting_capital={starting_capital}, risk_factor={risk_factor}, risk_reward={risk_reward}, slippage={slippage}, commission={commission}")
		print(f"[DEBUG] Initial chosen_provider: {provider}, timeframe: {timeframe}")
		if n_clicks == 0:
			empty_fig = go.Figure()
			win_loss_pie = go.Figure()
			return '', empty_fig, empty_fig, '', [], None, empty_fig, empty_fig, empty_fig, win_loss_pie
		fetcher = DataFetcher()
		ctx_inputs = callback_context.inputs
		timeframe = ctx_inputs.get('timeframe.value', '1d') if hasattr(ctx_inputs, 'get') else '1d'
		start_date = ctx_inputs.get('start-date.date', None)
		end_date = ctx_inputs.get('end-date.date', None)
		date_range = f"{start_date}_to_{end_date}" if start_date and end_date else None
		tf_map = {'1d': 'day', '1min': 'minute', '1m': 'minute', '5min': 'minute', '1h': 'hour'}
		chosen_provider = provider
		warning = ''
		def get_cache_timeframe(provider, timeframe):
			if provider == 'massive':
				return tf_map.get(timeframe, timeframe)
			return timeframe
		cache_timeframe = get_cache_timeframe(provider, timeframe)
		if provider == 'auto':
			print(f"[DEBUG] Provider is 'auto', evaluating timeframe logic for: {timeframe}")
			if timeframe in ['1m', '1min', 'minute']:
				print(f"[DEBUG] Timeframe is minute-based, start_date: {start_date}, end_date: {end_date}")
				if start_date and end_date:
					from datetime import datetime
					d0 = datetime.strptime(start_date, '%Y-%m-%d')
					d1 = datetime.strptime(end_date, '%Y-%m-%d')
					days = (d1 - d0).days + 1
					print(f"[DEBUG] Minute timeframe, days in range: {days}")
					if days <= 7:
						chosen_provider = 'yfinance'
						print(f"[DEBUG] Using yfinance for <=7 days")
					else:
						chosen_provider = 'massive'
						print(f"[DEBUG] Using massive for >7 days")
				else:
					chosen_provider = 'yfinance'
					print(f"[DEBUG] No date range, defaulting to yfinance")
			else:
				chosen_provider = 'massive'
				print(f"[DEBUG] Non-minute timeframe, using massive")
			cache_timeframe = get_cache_timeframe(chosen_provider, timeframe)
			print(f"[DEBUG] After auto logic, chosen_provider: {chosen_provider}, cache_timeframe: {cache_timeframe}")
		print(f"[DEBUG] selected_cache_file: {selected_cache_file}")
		print(f"[DEBUG] Final chosen_provider: {chosen_provider}, cache_timeframe: {cache_timeframe}")
		if selected_cache_file:
			project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
			cache_path = os.path.join(project_root, 'cache', str(chosen_provider), str(symbol), str(cache_timeframe), selected_cache_file)
			print(f"[DEBUG] Trying to load cache file: {cache_path}")
			if os.path.exists(cache_path):
				print(f"[DEBUG] Cache file exists: {cache_path}")
				data = pd.read_parquet(cache_path)
				date_range = os.path.splitext(selected_cache_file)[0]
			else:
				print(f"[DEBUG] Cache file does NOT exist: {cache_path}")
				data = None
		else:
			print(f"[DEBUG] Calling fetcher.cache.load with symbol={symbol}, provider={chosen_provider}, timeframe={cache_timeframe}, date_range={date_range}")
			data = fetcher.cache.load(symbol, chosen_provider, cache_timeframe, 'parquet', date_range)
			print(f"[DEBUG] fetcher.cache.load returned: {type(data)}")
			warning = f"No cached data for {symbol}/{chosen_provider}/{cache_timeframe}/{date_range}."
			empty_fig = go.Figure()
			win_loss_pie = go.Figure()
			return warning, empty_fig, empty_fig, '', [], None, empty_fig, empty_fig, empty_fig, win_loss_pie
		if data is None:
			warning = f"No data loaded for {symbol}/{chosen_provider}/{cache_timeframe}/{date_range}."
			empty_fig = go.Figure()
			win_loss_pie = go.Figure()
			return warning, empty_fig, empty_fig, '', [], None, empty_fig, empty_fig, empty_fig, win_loss_pie
		if strategy == 'sma_crossover':
			strat = SmaCrossoverStrategy(fast=fast, slow=slow)
		elif strategy == 'rsi_mean_reversion':
			strat = RsiMeanReversionStrategy()
		elif strategy == 'macd_crossover':
			strat = MACDCrossoverStrategy(fast=fast, slow=slow)
		elif strategy == 'impulse_macd':
			strat = ImpulseMACDStrategy(fast=fast, slow=slow, signal=9, hist_clip=0.5, lookback_days=22)
		else:
			empty_fig = go.Figure()
			win_loss_pie = go.Figure()
			return f"Unknown strategy: {strategy}", empty_fig, empty_fig, '', [], None, empty_fig, empty_fig, empty_fig, win_loss_pie
		backtester = Backtester(data, strat, initial_cash=starting_capital, fee=commission, risk_factor=risk_factor, risk_reward=risk_reward)
		results = backtester.run()
		results = compute_extra_metrics(backtester, results)
		# Use metrics_panel component
		settings = {
			'symbol': symbol,
			'provider': provider,
			'strategy': strategy,
			'fast': fast,
			'slow': slow,
			'starting_capital': starting_capital,
			'risk_factor': risk_factor,
			'risk_reward': risk_reward,
			'slippage': slippage,
			'commission': commission,
			'selected_cache_file': selected_cache_file
		}
		metrics = metrics_panel(settings, results)
		# Win/Loss Pie Chart
		win_loss_pie = go.Figure()
		if hasattr(backtester, 'trade_log') and not backtester.trade_log.empty:
			win_trades = (backtester.trade_log['pnl'] > 0).sum()
			loss_trades = (backtester.trade_log['pnl'] < 0).sum()
			win_loss_pie = go.Figure(data=[go.Pie(
				labels=['Winners', 'Losers'],
				values=[win_trades, loss_trades],
				marker=dict(colors=['#28a745', '#dc3545']),
				hole=0.4
			)])
			win_loss_pie.update_layout(title="Win/Loss Breakdown")
		# Prepare charts for biggest winner/loser
		biggest_win_fig = go.Figure()
		biggest_loss_fig = go.Figure()
		if 'biggest_win' in results:
			t = results['biggest_win']
			df = backtester.data.loc[t['entry']:t['exit']]
			biggest_win_fig.add_trace(go.Candlestick(
				x=df.index,
				open=df['open'], high=df['high'], low=df['low'], close=df['close'],
				name='Candles',
				increasing_line_color='green', decreasing_line_color='red',
			))
			biggest_win_fig.add_trace(go.Scatter(x=[t['entry']], y=[t['entry_price']], mode='markers', marker=dict(color='blue', size=12, symbol='star'), name='Entry'))
			biggest_win_fig.add_trace(go.Scatter(x=[t['exit']], y=[t['exit_price']], mode='markers', marker=dict(color='orange', size=12, symbol='x'), name='Exit'))
			if 'exit_reason' in t and isinstance(t['exit_reason'], str):
				biggest_win_fig.add_annotation(x=t['exit'], y=t['exit_price'],
											  text=f"Exit: {t['exit_reason']}",
											  showarrow=True, arrowhead=1, ax=0, ay=-40,
											  bgcolor="#fffbe6", bordercolor="#ff9900", borderpad=4)
			biggest_win_fig.update_layout(title=f"Biggest Winner: {t['entry']} → {t['exit']} ({t['exit_reason']})", xaxis_title='Date', yaxis_title='Price')
		if 'biggest_loss' in results:
			t = results['biggest_loss']
			df = backtester.data.loc[t['entry']:t['exit']]
			biggest_loss_fig.add_trace(go.Candlestick(
				x=df.index,
				open=df['open'], high=df['high'], low=df['low'], close=df['close'],
				name='Candles',
				increasing_line_color='green', decreasing_line_color='red',
			))
			biggest_loss_fig.add_trace(go.Scatter(x=[t['entry']], y=[t['entry_price']], mode='markers', marker=dict(color='blue', size=12, symbol='star'), name='Entry'))
			biggest_loss_fig.add_trace(go.Scatter(x=[t['exit']], y=[t['exit_price']], mode='markers', marker=dict(color='orange', size=12, symbol='x'), name='Exit'))
			if 'exit_reason' in t and isinstance(t['exit_reason'], str):
				biggest_loss_fig.add_annotation(x=t['exit'], y=t['exit_price'],
												text=f"Exit: {t['exit_reason']}",
												showarrow=True, arrowhead=1, ax=0, ay=-40,
												bgcolor="#fffbe6", bordercolor="#ff9900", borderpad=4)
			biggest_loss_fig.update_layout(title=f"Biggest Loser: {t['entry']} → {t['exit']} ({t['exit_reason']})", xaxis_title='Date', yaxis_title='Price')
		eq_fig = go.Figure()
		price_fig = go.Figure()
		if 'equity' in chart_toggles:
			eq_fig.add_trace(go.Scatter(x=backtester.data.index, y=backtester.data['equity'], mode='lines', name='Equity'))
			eq_fig.update_layout(title='Equity Curve', xaxis_title='Date', yaxis_title='Equity')
			ctx = callback_context
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
		trades = backtester._extract_trades()
		trade_table_html = trade_table(trades, backtester)
		trade_options = [
			{'label': f"{idx+1}: {str(t['entry'])[:10]} → {str(t['exit'])[:10]} ({'Long' if t['side']==1 else 'Short'})", 'value': idx}
			for idx, (_, t) in enumerate(trades.iterrows())
		]
		trade_value = selected_trade if selected_trade is not None else (0 if len(trade_options) > 0 else None)
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
			trade_fig.add_trace(go.Scatter(x=[entry], y=[df.loc[entry, 'close']], mode='markers', marker=dict(color='blue', size=12, symbol='star'), name='Entry'))
			trade_fig.add_trace(go.Scatter(x=[exit], y=[df.loc[exit, 'close']], mode='markers', marker=dict(color='orange', size=12, symbol='x'), name='Exit'))
			if 'exit_reason' in t and isinstance(t['exit_reason'], str):
				trade_fig.add_annotation(x=exit, y=df.loc[exit, 'close'],
										text=f"Exit: {t['exit_reason']}",
										showarrow=True, arrowhead=1, ax=0, ay=-40,
										bgcolor="#fffbe6", bordercolor="#ff9900", borderpad=4)
			trade_fig.update_layout(title=f"Trade {trade_value+1}: {entry} → {exit}", xaxis_title='Date', yaxis_title='Price')
		return metrics, eq_fig, price_fig, trade_table_html, trade_options, trade_value, trade_fig, biggest_win_fig, biggest_loss_fig, win_loss_pie

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
		import dash
		ctx_inputs = dash.callback_context.states
		timeframe = ctx_inputs.get('timeframe.value', '1d') if hasattr(ctx_inputs, 'get') else '1d'
		start_date = ctx_inputs.get('start-date.date', None)
		end_date = ctx_inputs.get('end-date.date', None)
		date_range = f"{start_date}_to_{end_date}" if start_date and end_date else None
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
		elif strategy == 'impulse_macd':
			strat = ImpulseMACDStrategy(fast=fast, slow=slow, signal=9, hist_clip=0.5, lookback_days=22)
		else:
			return no_update
		backtester = Backtester(data, strat)
		backtester.run()
		trades = backtester._extract_trades()
		if trades.empty:
			return no_update
		csv_string = trades.to_csv(index=False)
		return {
			'content': csv_string,
			'filename': f"trades_{symbol}_{provider}.csv",
			'type': 'text/csv'
		}

	# Update date range from cache

	@app.callback(
		[Output('start-date', 'date'), Output('end-date', 'date')],
		[Input('cache-file-dropdown', 'value')],
		[State('symbol', 'value'), State('provider', 'value'), State('timeframe', 'value')]
	)
	def update_dates_from_cache_file(cache_file, symbol, provider, timeframe):
		import os, re
		if not cache_file:
			return None, None
		# Try to extract date range from filename
		m = re.search(r'(\d{4}-\d{2}-\d{2})_to_(\d{4}-\d{2}-\d{2})', cache_file)
		if m:
			return m.group(1), m.group(2)
		return None, None


	# Helper function to get date range from cache directory
	def get_date_range_from_cache(symbol, provider, timeframe):
		import os
		import re
		tf_map = {'1d': 'day', '1min': 'minute', '1m': 'minute', '5min': 'minute', '1h': 'hour'}
		chosen_provider = 'massive' if provider in ['auto', 'massive'] else provider
		cache_timeframe = tf_map.get(timeframe, timeframe)
		project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
		cache_dir = os.path.join(project_root, 'cache', str(chosen_provider), str(symbol), str(cache_timeframe))
		if not os.path.isdir(cache_dir):
			return None, None
		files = [f for f in os.listdir(cache_dir) if f.endswith('.parquet')]
		for f in sorted(files):
			m = re.search(r'(\d{4}-\d{2}-\d{2})_to_(\d{4}-\d{2}-\d{2})', f)
			if m:
				return m.group(1), m.group(2)
		return None, None

	def update_date_range(symbol, provider, timeframe):
		start, end = get_date_range_from_cache(symbol, provider, timeframe)
		if not start or not end:
			return None, None
		return start, end
