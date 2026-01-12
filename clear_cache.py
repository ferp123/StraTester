"""
clear_cache.py

Clear cached market data for specified provider, symbol(s), and timeframe(s).
Set parameters below and run the script directly.
"""
import os
import shutil

# === PARAMETERS ===
PROVIDER = 'massive'  # e.g. 'massive', 'yfinance'
SYMBOLS = 'all'       # Comma-separated string or 'all'
TIMEFRAMES = '1d'     # Comma-separated string or 'all'

CACHE_ROOT = os.path.join(os.path.dirname(__file__), 'cache')

def clear_cache(provider, symbols, timeframes):
    provider_path = os.path.join(CACHE_ROOT, provider)
    if not os.path.exists(provider_path):
        print(f"No cache found for provider: {provider}")
        return
    # Handle 'all' for symbols
    if symbols == ['all']:
        symbol_list = [d for d in os.listdir(provider_path) if os.path.isdir(os.path.join(provider_path, d))]
    else:
        symbol_list = symbols
    for symbol in symbol_list:
        symbol_path = os.path.join(provider_path, symbol)
        if not os.path.exists(symbol_path):
            print(f"No cache found for symbol: {symbol} (provider: {provider})")
            continue
        # Handle 'all' for timeframes
        if timeframes == ['all']:
            # Always include 'parquet' subfolder if present
            timeframe_list = [d for d in os.listdir(symbol_path) if os.path.isdir(os.path.join(symbol_path, d))]
            if 'parquet' not in timeframe_list and os.path.isdir(os.path.join(symbol_path, 'parquet')):
                timeframe_list.append('parquet')
        else:
            timeframe_list = timeframes
        for timeframe in timeframe_list:
            timeframe_path = os.path.join(symbol_path, timeframe)
            if os.path.exists(timeframe_path):
                print(f"Clearing cache: {timeframe_path}")
                shutil.rmtree(timeframe_path)
            else:
                print(f"No cache found for timeframe: {timeframe} (symbol: {symbol}, provider: {provider})")

if __name__ == "__main__":
    symbols = [s.strip() for s in SYMBOLS.split(',')]
    if isinstance(TIMEFRAMES, str):
        timeframes = [t.strip() for t in TIMEFRAMES.split(',')]
    elif isinstance(TIMEFRAMES, (list, tuple)):
        timeframes = list(TIMEFRAMES)
    else:
        raise ValueError("TIMEFRAMES must be a string, list, or tuple")
    clear_cache(PROVIDER, symbols, timeframes)
