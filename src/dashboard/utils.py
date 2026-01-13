
import numpy as np
from dash import html

def compute_extra_metrics(backtester, results):
	# Biggest winner/loser
	if hasattr(backtester, 'trade_log') and not backtester.trade_log.empty:
		biggest_win = backtester.trade_log.loc[backtester.trade_log['pnl'].idxmax()]
		biggest_loss = backtester.trade_log.loc[backtester.trade_log['pnl'].idxmin()]
		results['biggest_win'] = biggest_win
		results['biggest_loss'] = biggest_loss
	equity = backtester.data['equity']
	returns = backtester.data['strategy_returns']
	n_years = (equity.index[-1] - equity.index[0]).days / 365.25
	cagr = (equity.iloc[-1] / equity.iloc[0]) ** (1 / n_years) - 1 if n_years > 0 else np.nan
	if hasattr(backtester, 'trade_log') and not backtester.trade_log.empty:
		num_trades = len(backtester.trade_log)
		win_trades = (backtester.trade_log['pnl'] > 0).sum()
		loss_trades = (backtester.trade_log['pnl'] < 0).sum()
		win_rate = win_trades / num_trades if num_trades > 0 else np.nan
		avg_win = backtester.trade_log[backtester.trade_log['pnl'] > 0]['pnl'].mean()
		avg_loss = backtester.trade_log[backtester.trade_log['pnl'] < 0]['pnl'].mean()
	else:
		num_trades = 0
		win_trades = 0
		loss_trades = 0
		win_rate = np.nan
		avg_win = np.nan
		avg_loss = np.nan
	avg_trade = returns.mean()
	results['CAGR'] = cagr
	results['win_rate'] = win_rate
	results['avg_trade'] = avg_trade
	results['num_trades'] = num_trades
	results['avg_win'] = avg_win
	results['avg_loss'] = avg_loss
	return results

def trades_to_table(trades, backtester):
	if hasattr(backtester, 'trade_log') and not backtester.trade_log.empty:
		rows = []
		for _, t in backtester.trade_log.iterrows():
			rows.append(html.Tr([
				html.Td(str(t['entry'])),
				html.Td(str(t['exit'])),
				html.Td('Long' if t['side'] == 1 else 'Short'),
				html.Td(f"{t['entry_price']:.2f}" if t['entry_price'] else ''),
				html.Td(f"{t['exit_price']:.2f}" if t['exit_price'] else ''),
				html.Td(f"{t['pnl']:.2f}" if t['pnl'] else ''),
				html.Td(t['exit_reason']),
			]))
		return html.Table([
			html.Thead(html.Tr([html.Th(h) for h in ['Entry', 'Exit', 'Side', 'Entry Price', 'Exit Price', 'PnL', 'Exit Reason']])),
			html.Tbody(rows)
		], style={'width': '100%', 'border': '1px solid #ccc'})
	else:
		return html.Div("No trades.")
