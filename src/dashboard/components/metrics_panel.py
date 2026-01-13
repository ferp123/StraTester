
from dash import html

def metrics_panel(settings, results):
	return html.Div([
		html.Div([
			html.H5("Backtest Settings"),
			html.Ul([
				html.Li(f"Symbol: {settings.get('symbol')}") if settings.get('symbol') else None,
				html.Li(f"Provider: {settings.get('provider')}") if settings.get('provider') else None,
				html.Li(f"Strategy: {settings.get('strategy')}") if settings.get('strategy') else None,
				html.Li(f"Fast: {settings.get('fast')}") if settings.get('fast') is not None else None,
				html.Li(f"Slow: {settings.get('slow')}") if settings.get('slow') is not None else None,
				html.Li(f"Starting Capital: {settings.get('starting_capital')}") if settings.get('starting_capital') else None,
				html.Li(f"Risk Factor: {settings.get('risk_factor')}") if settings.get('risk_factor') else None,
				html.Li(f"Risk/Reward: {settings.get('risk_reward')}") if settings.get('risk_reward') else None,
				html.Li(f"Slippage: {settings.get('slippage')}") if settings.get('slippage') is not None else None,
				html.Li(f"Commission: {settings.get('commission')}") if settings.get('commission') is not None else None,
				html.Li(f"Cache File: {settings.get('selected_cache_file')}") if settings.get('selected_cache_file') else None,
			])
		], style={"flex": "1", "margin-right": "32px", "minWidth": "220px"}),
		html.Div([
			html.H5("Test Results"),
			html.Ul([
				html.Li(f"Final Equity: {results.get('final_equity', 0):.2f}"),
				html.Li(f"Total Return: {results.get('total_return', 0):.2%}"),
				html.Li(f"Max Drawdown: {results.get('max_drawdown', 0):.2%}"),
				html.Li(f"Sharpe Ratio: {results.get('sharpe', 0):.2f}"),
				html.Li(f"CAGR: {results.get('CAGR', 0):.2%}"),
				html.Li(f"Win Rate: {results.get('win_rate', 0):.2%}"),
				html.Li(f"Avg Trade: {results.get('avg_trade', 0):.4f}"),
				html.Li(f"Avg Win: {results.get('avg_win', 0):.2f}"),
				html.Li(f"Avg Loss: {results.get('avg_loss', 0):.2f}"),
				html.Li(f"Number of Trades: {results.get('num_trades', 0)}"),
				html.Li(f"Biggest Winner: {results.get('biggest_win', {}).get('pnl', 'N/A'):.2f}" if 'biggest_win' in results else "Biggest Winner: N/A"),
				html.Li(f"Biggest Loser: {results.get('biggest_loss', {}).get('pnl', 'N/A'):.2f}" if 'biggest_loss' in results else "Biggest Loser: N/A"),
			])
		], style={"flex": "1", "minWidth": "220px"}),
	], style={"display": "flex", "flex-direction": "row", "align-items": "flex-start", "gap": "16px"})
