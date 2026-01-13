"""
Impulse MACD Strategy for StrategyTester
"""
import pandas as pd
import numpy as np
from strategy_interface import Strategy

class ImpulseMACDStrategy(Strategy):
    def __init__(self, fast=12, slow=26, signal=9, hist_clip=0.5, lookback_days=22):
        self.fast = fast
        self.slow = slow
        self.signal = signal
        self.hist_clip = hist_clip
        self.lookback_days = lookback_days

    def _dynamic_hist_threshold(self, macd_hist):
        # Use rolling 90th/10th percentiles, clipped to +/- hist_clip
        upper = np.clip(np.percentile(macd_hist, 90), 0, self.hist_clip)
        lower = np.clip(np.percentile(macd_hist, 10), -self.hist_clip, 0)
        return upper, lower

    def _find_oversold_overbought(self, macd_line, window=22):
        # Find 3-4 highest peaks and lowest troughs in the lookback window
        peaks = macd_line[-window:].nlargest(4)
        troughs = macd_line[-window:].nsmallest(4)
        # Exclude the absolute max/min, average the next 3
        overbought = peaks.iloc[1:].mean() if len(peaks) > 1 else peaks.mean()
        oversold = troughs.iloc[:-1].mean() if len(troughs) > 1 else troughs.mean()
        return oversold, overbought

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        df['ema_fast'] = df['close'].ewm(span=self.fast, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=self.slow, adjust=False).mean()
        df['macd'] = df['ema_fast'] - df['ema_slow']
        df['macd_signal'] = df['macd'].ewm(span=self.signal, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        signals = []
        for i in range(len(df)):
            if i < self.lookback_days:
                signals.append(0)
                continue
            # Dynamic histogram breakout
            hist_window = df['macd_hist'].iloc[i-self.lookback_days:i]
            upper, lower = self._dynamic_hist_threshold(hist_window)
            # Dynamic oversold/overbought
            macd_window = df['macd'].iloc[i-self.lookback_days:i]
            oversold, overbought = self._find_oversold_overbought(macd_window, self.lookback_days)
            macd = df['macd'].iloc[i]
            hist = df['macd_hist'].iloc[i]
            # Breakout
            if hist > upper:
                signals.append(1)
            elif hist < lower:
                signals.append(-1)
            # Reversal (oversold/overbought)
            elif macd < oversold:
                signals.append(1)
            elif macd > overbought:
                signals.append(-1)
            else:
                signals.append(0)
        df['signal'] = signals
        return df[['signal']]

    def custom_metrics(self, trades, data):
        # Add custom Impulse MACD metrics if desired
        return {}
