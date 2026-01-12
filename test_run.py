"""
Test script: Run SMA Crossover strategy on cached Massive data for GOOGL
"""

import pandas as pd
from src.data_fetchers import DataFetcher
from src.strategies.sma_crossover import SmaCrossoverStrategy
from src.backtester import Backtester

# Load cached data (simulate fetch)
fetcher = DataFetcher()
data = fetcher.cache.load('GOOGL', 'massive', 'parquet')

if data is None:
    print("No cached data found for GOOGL/massive. Please run the fetcher first.")
else:
    # Run SMA Crossover strategy
    strategy = SmaCrossoverStrategy(fast=5, slow=15)
    backtester = Backtester(data, strategy)
    results = backtester.run()
    print("Backtest Results:")
    for k, v in results.items():
        print(f"{k}: {v}")
