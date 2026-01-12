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
    'macd_crossover': 'src.strategies.macd_crossover.MACDCrossoverStrategy',
    'impulse_macd': 'src.strategies.impulse_macd.ImpulseMACDStrategy',
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
    parser.add_argument('--risk_factor', type=float, default=1.0, help='Risk factor (multiplier for risk per trade, e.g. 1 = 1% of equity)')
    parser.add_argument('--risk_reward', type=float, default=3.0, help='Risk:Reward ratio (e.g. 3 = 3:1)')
    parser.add_argument('--timeframe', type=str, default='1d', help='Timeframe (e.g. 1d, 1min, 5min, 1h)')
    parser.add_argument('--date_range', type=str, default=None, help='Date range string (e.g. 2021-01-01_to_2026-01-12)')
    args = parser.parse_args()

    fetcher = DataFetcher()
    # Timeframe mapping for cache folder
    tf_map = {'1d': 'day', '1min': 'minute', '1m': 'minute', '5min': 'minute', '1h': 'hour'}
    cache_timeframe = args.timeframe or '1d'
    if args.provider == 'massive':
        cache_timeframe = tf_map.get(args.timeframe, 'day')
    data = fetcher.cache.load(args.symbol, args.provider, cache_timeframe, 'parquet', args.date_range)
    if data is None:
        print(f"No cached data found for {args.symbol}/{args.provider}/{cache_timeframe}{f'/{args.date_range}' if args.date_range else ''}. Please run the fetcher first.")
        return

    StrategyClass = get_strategy_class(args.strategy)
    # For impulse_macd, pass extra params
    if args.strategy == 'impulse_macd':
        strategy = StrategyClass(fast=args.fast, slow=args.slow, signal=9, hist_clip=0.5, lookback_days=22)
    else:
        strategy = StrategyClass(fast=args.fast, slow=args.slow)
    backtester = Backtester(
        data, strategy, initial_cash=args.cash, fee=args.fee,
        risk_factor=args.risk_factor, risk_reward=args.risk_reward
    )
    results = backtester.run()
    print("Backtest Results:")
    for k, v in results.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    main()
