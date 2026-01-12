"""
Vectorized Backtesting Engine for StrategyTester
Runs strategies on historical data and computes performance metrics.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from .strategy_interface import Strategy

class Backtester:
    def __init__(self, data: pd.DataFrame, strategy: Strategy, initial_cash: float = 100_000, fee: float = 0.0):
        self.data = data.copy()
        self.strategy = strategy
        self.initial_cash = initial_cash
        self.fee = fee
        self.results = {}

    def run(self) -> Dict[str, Any]:
        # Pre-backtest hook
        self.strategy.before_backtest(self.data)
        # Generate signals
        signals = self.strategy.generate_signals(self.data)
        self.data = self.data.join(signals, how='left')
        self.data['signal'] = self.data['signal'].fillna(0)
        # Calculate positions (simple: 1=long, -1=short, 0=flat)
        self.data['position'] = self.data['signal'].shift(1).fillna(0)
        # Calculate returns
        self.data['returns'] = self.data['close'].pct_change().fillna(0)
        self.data['strategy_returns'] = self.data['returns'] * self.data['position']
        # Calculate equity curve
        self.data['equity'] = self.initial_cash * (1 + self.data['strategy_returns']).cumprod()
        # Track trades
        trades = self._extract_trades()
        # Compute metrics
        metrics = self._compute_metrics(trades)
        # Custom metrics
        metrics.update(self.strategy.custom_metrics(trades, self.data))
        # Post-backtest hook
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
        metrics = {
            'final_equity': equity.iloc[-1],
            'total_return': equity.iloc[-1] / self.initial_cash - 1,
            'max_drawdown': self._max_drawdown(equity),
            'sharpe': self._sharpe(returns),
            'num_trades': len(trades),
        }
        return metrics

    def _max_drawdown(self, equity: pd.Series) -> float:
        roll_max = equity.cummax()
        drawdown = (equity - roll_max) / roll_max
        return drawdown.min()

    def _sharpe(self, returns: pd.Series, risk_free: float = 0.0) -> float:
        excess = returns - risk_free / 252
        return np.sqrt(252) * excess.mean() / (excess.std() + 1e-9)
