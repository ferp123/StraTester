"""
Vectorized Backtesting Engine for StrategyTester
Runs strategies on historical data and computes performance metrics.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from strategy_interface import Strategy

class Backtester:
    def __init__(self, data: pd.DataFrame, strategy: Strategy, initial_cash: float = 100_000, fee: float = 0.0, risk_factor: float = 1.0, risk_reward: float = 3.0):
        self.data = data.copy()
        self.strategy = strategy
        self.initial_cash = initial_cash
        self.fee = fee
        self.risk_factor = risk_factor
        self.risk_reward = risk_reward
        self.results = {}

    def run(self) -> Dict[str, Any]:
        self.strategy.before_backtest(self.data)
        signals = self.strategy.generate_signals(self.data)
        self.data = self.data.join(signals, how='left')
        self.data['signal'] = self.data['signal'].fillna(0)
        self.data['position'] = self.data['signal'].shift(1).fillna(0)
        self.data['returns'] = self.data['close'].pct_change().fillna(0)

        # New: SL/TP and position sizing logic
        equity = self.initial_cash
        position = 0
        entry_price = None
        stop_loss = None
        take_profit = None
        trade_size = 0
        equity_curve = []
        strat_returns = []
        trade_info = []
        trade_log = []
        entry_idx = None
        for i, (idx, row) in enumerate(self.data.iterrows()):
            signal = row['signal']
            price = row['close']
            # Exit logic
            exit_reason = None
            if position != 0:
                # Check SL/TP
                if position == 1:
                    if price <= stop_loss:
                        exit_reason = 'stop_loss'
                    elif price >= take_profit:
                        exit_reason = 'take_profit'
                elif position == -1:
                    if price >= stop_loss:
                        exit_reason = 'stop_loss'
                    elif price <= take_profit:
                        exit_reason = 'take_profit'
                # Exit on opposite signal
                if signal == -position and exit_reason is None:
                    exit_reason = 'signal'
                if exit_reason:
                    # Close trade
                    pnl = (price - entry_price) * position * trade_size - self.fee
                    equity += pnl
                    trade_log.append({
                        'entry': entry_idx,
                        'exit': idx,
                        'side': position,
                        'entry_price': entry_price,
                        'exit_price': price,
                        'size': trade_size,
                        'pnl': pnl,
                        'exit_reason': exit_reason
                    })
                    position = 0
                    entry_price = None
                    stop_loss = None
                    take_profit = None
                    trade_size = 0
                    trade_info.append({'exit': idx, 'exit_reason': exit_reason, 'pnl': pnl, 'equity': equity})
                    entry_idx = None
            # Entry logic
            if position == 0 and signal != 0:
                # Risk per trade: risk_factor% of equity
                risk_per_trade = self.risk_factor / 100 * equity
                # Set stop loss 1% away from entry (default, can be improved)
                sl_pct = 0.01
                if signal == 1:
                    stop_loss = price * (1 - sl_pct)
                    take_profit = price + (price - stop_loss) * self.risk_reward
                else:
                    stop_loss = price * (1 + sl_pct)
                    take_profit = price - (stop_loss - price) * self.risk_reward
                # Position size = risk per trade / (entry - stop_loss)
                risk_per_share = abs(price - stop_loss)
                trade_size = risk_per_trade / risk_per_share if risk_per_share > 0 else 0
                entry_price = price
                position = signal
                entry_idx = idx
                trade_info.append({'entry': idx, 'entry_price': price, 'size': trade_size, 'stop_loss': stop_loss, 'take_profit': take_profit, 'equity': equity})
            # Mark-to-market
            if position != 0 and entry_price is not None:
                mtm_pnl = (price - entry_price) * position * trade_size
                equity_curve.append(equity + mtm_pnl)
                strat_returns.append(mtm_pnl / (equity if equity else 1))
            else:
                equity_curve.append(equity)
                strat_returns.append(0)
        self.data['equity'] = equity_curve
        self.data['strategy_returns'] = strat_returns
        self.trade_log = pd.DataFrame(trade_log)
        trades = self._extract_trades()
        metrics = self._compute_metrics(trades)
        # Add average win/loss
        if not self.trade_log.empty:
            wins = self.trade_log[self.trade_log['pnl'] > 0]['pnl']
            losses = self.trade_log[self.trade_log['pnl'] < 0]['pnl']
            metrics['avg_win'] = wins.mean() if not wins.empty else 0
            metrics['avg_loss'] = losses.mean() if not losses.empty else 0
        else:
            metrics['avg_win'] = 0
            metrics['avg_loss'] = 0
        metrics.update(self.strategy.custom_metrics(trades, self.data))
        self.strategy.after_backtest(metrics)
        self.results = metrics
        return metrics

    def _extract_trades(self) -> pd.DataFrame:
        # Find trade entry/exit points
        trades = []
        pos = 0
        entry_idx = None
        for idx, row in self.data.iterrows():
            if row['position'] != pos:
                if pos != 0:
                    # Exit trade
                    trades.append({'entry': entry_idx, 'exit': idx, 'side': pos})
                if row['position'] != 0:
                    # Enter trade
                    entry_idx = idx
                pos = row['position']
        return pd.DataFrame(trades)

    def _compute_metrics(self, trades: pd.DataFrame) -> Dict[str, Any]:
        equity = self.data['equity']
        returns = self.data['strategy_returns']
        # Use trade_log for number of trades if available
        num_trades = len(self.trade_log) if hasattr(self, 'trade_log') and not self.trade_log.empty else len(trades)
        metrics = {
            'final_equity': equity.iloc[-1],
            'total_return': equity.iloc[-1] / self.initial_cash - 1,
            'max_drawdown': self._max_drawdown(equity),
            'sharpe': self._sharpe(returns),
            'num_trades': num_trades,
        }
        return metrics

    def _max_drawdown(self, equity: pd.Series) -> float:
        roll_max = equity.cummax()
        drawdown = (equity - roll_max) / roll_max
        return drawdown.min()

    def _sharpe(self, returns: pd.Series, risk_free: float = 0.0) -> float:
        excess = returns - risk_free / 252
        return np.sqrt(252) * excess.mean() / (excess.std() + 1e-9)
