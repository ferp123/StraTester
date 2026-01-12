"""
Abstract base class for trading strategies in the StrategyTester framework.
Defines the interface and hooks for vectorized, extensible strategies.
"""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

class Strategy(ABC):
    def __init__(self, params: Optional[Dict[str, Any]] = None):
        """
        Initialize the strategy with optional parameters.
        """
        self.params = params or {}
        self.results = {}

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals (1=buy, -1=sell, 0=hold) for each row in the data.
        Must return a DataFrame with the same index as data and at least a 'signal' column.
        """
        pass

    def before_backtest(self, data: pd.DataFrame) -> None:
        """
        Optional hook: Called before backtest starts. Can be used for preprocessing or feature engineering.
        """
        pass

    def after_backtest(self, results: Dict[str, Any]) -> None:
        """
        Optional hook: Called after backtest ends. Can be used for logging, analysis, or storing results.
        """
        self.results = results

    def optimize(self, data: pd.DataFrame, param_grid: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optional hook: Run parameter optimization. Should return the best parameter set and score.
        """
        # Example: grid search (to be implemented in concrete class)
        raise NotImplementedError("Parameter optimization not implemented.")

    def custom_metrics(self, trades: pd.DataFrame, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Optional hook: Compute custom metrics after backtest.
        """
        return {}

    def on_trade(self, trade: Dict[str, Any]) -> None:
        """
        Optional hook: Called on each trade event (entry/exit). Useful for logging or custom logic.
        """
        pass

    def on_bar(self, bar: pd.Series) -> None:
        """
        Optional hook: Called on each bar (row) of data during backtest.
        """
        pass
