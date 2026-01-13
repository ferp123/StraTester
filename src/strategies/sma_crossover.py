"""
Sample strategy: Simple Moving Average (SMA) Crossover
Implements the Strategy interface for demonstration and testing.
"""

import pandas as pd
from typing import Dict, Any
from strategy_interface import Strategy

class SmaCrossoverStrategy(Strategy):
    def __init__(self, fast: int = 10, slow: int = 30, **kwargs):
        params = {'fast': fast, 'slow': slow}
        params.update(kwargs)
        super().__init__(params)
        self.fast = fast
        self.slow = slow

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        df['sma_fast'] = df['close'].rolling(window=self.fast, min_periods=1).mean()
        df['sma_slow'] = df['close'].rolling(window=self.slow, min_periods=1).mean()
        df['signal'] = 0
        df.loc[df['sma_fast'] > df['sma_slow'], 'signal'] = 1
        df.loc[df['sma_fast'] < df['sma_slow'], 'signal'] = -1
        return df[['signal', 'sma_fast', 'sma_slow']]

    def custom_metrics(self, trades: pd.DataFrame, data: pd.DataFrame) -> Dict[str, Any]:
        # Example: count trades
        return {'num_trades': len(trades)}
