"""
MACD Crossover Strategy for StrategyTester
"""
import pandas as pd
import numpy as np
from src.strategy_interface import Strategy

class MACDCrossoverStrategy(Strategy):
    def __init__(self, fast=12, slow=26, signal=9):
        self.fast = fast
        self.slow = slow
        self.signal = signal

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        df['ema_fast'] = df['close'].ewm(span=self.fast, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=self.slow, adjust=False).mean()
        df['macd'] = df['ema_fast'] - df['ema_slow']
        df['macd_signal'] = df['macd'].ewm(span=self.signal, adjust=False).mean()
        # Signal: 1 for MACD crosses above signal, -1 for crosses below
        df['signal'] = np.where(df['macd'] > df['macd_signal'], 1,
                                np.where(df['macd'] < df['macd_signal'], -1, 0))
        return df[['signal']]

    def custom_metrics(self, trades, data):
        # Add custom MACD metrics if desired
        return {}
