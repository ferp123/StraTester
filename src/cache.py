"""
Local caching utilities for market data.
Supports parquet, csv, and feather formats.
Provides a DataCache class to save and load DataFrames efficiently for each symbol/provider.
"""
import os
import pandas as pd
from typing import Optional

CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

class DataCache:
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the DataCache with a cache directory.
        :param cache_dir: Optional custom cache directory path
        """
        self.cache_dir = cache_dir or CACHE_DIR
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_path(self, symbol: str, provider: str, ext: str) -> str:
        """
        Build the cache file path for a given symbol, provider, and file extension.
        :param symbol: Stock ticker symbol
        :param provider: Data provider name (e.g., yfinance, alpaca, massive)
        :param ext: File extension (parquet, csv, feather)
        :return: Full path to the cache file
        """
        fname = f"{symbol}_{provider}.{ext}"
        return os.path.join(self.cache_dir, fname)

    def save(self, df: pd.DataFrame, symbol: str, provider: str, fmt: str = 'parquet'):
        """
        Save a DataFrame to the cache in the specified format.
        :param df: DataFrame to save
        :param symbol: Stock ticker symbol
        :param provider: Data provider name
        :param fmt: File format (parquet, csv, feather)
        """
        path = self._get_path(symbol, provider, fmt)
        if fmt == 'parquet':
            df.to_parquet(path)
        elif fmt == 'csv':
            df.to_csv(path)
        elif fmt == 'feather':
            df.reset_index().to_feather(path)
        else:
            raise ValueError(f"Unsupported format: {fmt}")

    def load(self, symbol: str, provider: str, fmt: str = 'parquet') -> Optional[pd.DataFrame]:
        """
        Load a DataFrame from the cache if it exists.
        :param symbol: Stock ticker symbol
        :param provider: Data provider name
        :param fmt: File format (parquet, csv, feather)
        :return: DataFrame if found, else None
        """
        path = self._get_path(symbol, provider, fmt)
        if not os.path.exists(path):
            return None
        if fmt == 'parquet':
            return pd.read_parquet(path)
        elif fmt == 'csv':
            return pd.read_csv(path, index_col=0, parse_dates=True)
        elif fmt == 'feather':
            df = pd.read_feather(path)
            if 'datetime' in df.columns:
                df.set_index('datetime', inplace=True)
            return df
        else:
            raise ValueError(f"Unsupported format: {fmt}")
