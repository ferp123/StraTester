"""
Sample strategy: RSI Mean Reversion
Buys when RSI < 30, sells when RSI > 70.
Implements the Strategy interface.
"""

import pandas as pd
from typing import Dict, Any
from strategy_interface import Strategy

class RsiMeanReversionStrategy(Strategy):
    def __init__(self, period: int = 14, lower: float = 30, upper: float = 70, trend_ma: int = 50, **kwargs):
        params = {'period': period, 'lower': lower, 'upper': upper, 'trend_ma': trend_ma}
        params.update(kwargs)
        super().__init__(params)
        self.period = period
        self.lower = lower
        self.upper = upper
        self.trend_ma = trend_ma

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        delta = df['close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(self.period, min_periods=1).mean()
        avg_loss = loss.rolling(self.period, min_periods=1).mean()
        rs = avg_gain / (avg_loss + 1e-9)
        df['rsi'] = 100 - (100 / (1 + rs))
        df['signal'] = 0
        # Trend filter: only allow shorts if price is below MA
        df['ma'] = df['close'].rolling(self.trend_ma, min_periods=1).mean()
        df.loc[df['rsi'] < self.lower, 'signal'] = 1
        df.loc[(df['rsi'] > self.upper) & (df['close'] < df['ma']), 'signal'] = -1
        return df[['signal', 'rsi']]

    def custom_metrics(self, trades: pd.DataFrame, data: pd.DataFrame) -> Dict[str, Any]:
        return {'num_trades': len(trades)}
