
from dash import html

def trade_table(trades, backtester):
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
