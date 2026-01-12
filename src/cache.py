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

    def _get_path(self, symbol: str, provider: str, timeframe: str = '1d', ext: str = 'parquet', date_range: Optional[str] = None) -> str:
        """
        Build the cache file path for a given symbol, provider, timeframe, and file extension.
        :param symbol: Stock ticker symbol
        :param provider: Data provider name (e.g., yfinance, massive)
        :param timeframe: Data timeframe (e.g., '1d', '1min')
        :param ext: File extension (parquet, csv, feather)
        :param date_range: Optional date range string (e.g., '2019-2026')
        :return: Full path to the cache file
        """
        # Guard: For massive, only allow mapped timeframes
        if provider == 'massive':
            allowed = {'day', 'minute', 'hour'}
            if timeframe not in allowed:
                raise ValueError(f"[DataCache] Invalid timeframe '{timeframe}' for provider 'massive'. Only {allowed} are allowed. Please use the correct mapping.")
        folder = os.path.join(self.cache_dir, provider, symbol, timeframe)
        os.makedirs(folder, exist_ok=True)
        fname = f"{date_range}.{ext}" if date_range else f"data.{ext}"
        return os.path.join(folder, fname)

    def save(self, df: pd.DataFrame, symbol: str, provider: str, timeframe: str = '1d', fmt: str = 'parquet', date_range: Optional[str] = None):
        """
        Save a DataFrame to the cache in the specified format and structure.
        :param df: DataFrame to save
        :param symbol: Stock ticker symbol
        :param provider: Data provider name
        :param timeframe: Data timeframe (e.g., '1d', '1min')
        :param fmt: File format (parquet, csv, feather)
        :param date_range: Optional date range string
        """
        path = self._get_path(symbol, provider, timeframe, fmt, date_range)
        if fmt == 'parquet':
            df.to_parquet(path)
        elif fmt == 'csv':
            df.to_csv(path)
        elif fmt == 'feather':
            df.reset_index().to_feather(path)
        else:
            raise ValueError(f"Unsupported format: {fmt}")

    def load(self, symbol: str, provider: str, timeframe: str = '1d', fmt: str = 'parquet', date_range: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Load a DataFrame from the cache if it exists.
        :param symbol: Stock ticker symbol
        :param provider: Data provider name
        :param timeframe: Data timeframe (e.g., '1d', '1min')
        :param fmt: File format (parquet, csv, feather)
        :param date_range: Optional date range string
        :return: DataFrame if found, else None
        """
        path = self._get_path(symbol, provider, timeframe, fmt, date_range)
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
