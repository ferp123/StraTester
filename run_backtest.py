"""
CLI tool to run backtests on cached data with any strategy.
Usage example:
python run_backtest.py --symbol GOOGL --provider massive --strategy sma_crossover --fast 5 --slow 15
"""

import argparse
import importlib
from src.data_fetchers import DataFetcher
from src.backtester import Backtester

STRATEGY_MAP = {
    'sma_crossover': 'src.strategies.sma_crossover.SmaCrossoverStrategy',
    'rsi_mean_reversion': 'src.strategies.rsi_mean_reversion.RsiMeanReversionStrategy',
}

def get_strategy_class(strategy_name):
    if strategy_name not in STRATEGY_MAP:
        raise ValueError(f"Unknown strategy: {strategy_name}")
    module_path, class_name = STRATEGY_MAP[strategy_name].rsplit('.', 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)

def main():
    parser = argparse.ArgumentParser(description="Run a backtest on cached data.")
    parser.add_argument('--symbol', required=True, help='Ticker symbol (e.g. GOOGL)')
    parser.add_argument('--provider', required=True, choices=['massive', 'yfinance'], help='Data provider')
    parser.add_argument('--strategy', required=True, choices=list(STRATEGY_MAP.keys()), help='Strategy name')
    parser.add_argument('--fast', type=int, default=5, help='Fast period (for SMA Crossover)')
    parser.add_argument('--slow', type=int, default=15, help='Slow period (for SMA Crossover)')
    parser.add_argument('--cash', type=float, default=100_000, help='Initial cash')
    parser.add_argument('--fee', type=float, default=0.0, help='Per-trade fee')
    args = parser.parse_args()

    fetcher = DataFetcher()
    data = fetcher.cache.load(args.symbol, args.provider, 'parquet')
    if data is None:
        print(f"No cached data found for {args.symbol}/{args.provider}. Please run the fetcher first.")
        return

    StrategyClass = get_strategy_class(args.strategy)
    strategy = StrategyClass(fast=args.fast, slow=args.slow)
    backtester = Backtester(data, strategy, initial_cash=args.cash, fee=args.fee)
    results = backtester.run()
    print("Backtest Results:")
    for k, v in results.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    main()
