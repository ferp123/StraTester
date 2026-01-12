"""
fetch_bulk_data.py

Fetches and caches historical market data for a list of symbols, timeframes, and date ranges using yFinance (or Massive if desired).
- Easy to adjust symbols, timeframes, and date ranges.
- Checks cache before fetching to avoid redundant downloads.
- Handles yFinance 1m limitations (only last 7 days allowed).
"""
import os
from datetime import datetime, timedelta
from src.data_fetchers import DataFetcher

# === CONFIGURATION ===
SYMBOLS = [
     'AAPL', 
     'MSFT', 
     'UNH', 
     'JNJ', 
     'JPM', 
     'BAC', 
     'AMZN', 
     'TSLA', 
     'BA', 
     'UNP',
     'SPY',
     'GOOGL'
]
PROVIDER = 'massive'  # 'yfinance' or 'massive'
TIMEFRAMES = {
    '1d': {
        'start': '2021-01-01',
        'end': datetime.today().strftime('%Y-%m-%d')
    },
    '1m': {
        'start': (datetime.today() - timedelta(days=180)).strftime('%Y-%m-%d'),
        'end': datetime.today().strftime('%Y-%m-%d')
    }
}

CACHE_FMT = 'parquet'

YF_1M_MAX_DAYS = 7  # yFinance only allows 7 days of 1m data per request, and only for recent dates

MASSIVE_TIMEFRAME_MAP = {
    '1d': 'day',
    '1m': 'minute',
    '1h': 'hour',
    '5min': 'minute',  # Polygon supports 'minute', not '5min', so you may need to filter after fetch
}

def main():
    fetcher = DataFetcher(cache_fmt=CACHE_FMT)
    import time
    MAX_RETRIES = 5
    DELAY_SECONDS = 15
    for symbol in SYMBOLS:
        for timeframe, dates in TIMEFRAMES.items():
            start = dates['start']
            end = dates['end']
            date_range = f"{start}_to_{end}"
            # yFinance 1m limitation: only fetch last 7 days (inclusive)
            if PROVIDER == 'yfinance' and timeframe == '1m':
                start_dt = datetime.strptime(start, '%Y-%m-%d')
                end_dt = datetime.strptime(end, '%Y-%m-%d')
                today = datetime.today()
                delta_start = (today - start_dt).days
                delta_end = (today - end_dt).days
                if delta_start > (YF_1M_MAX_DAYS - 1) or delta_end < 0:
                    print(f"[SKIP] {symbol} 1m {start} to {end}: yFinance only allows 1m data for the last 7 days (inclusive).")
                    continue
            # Always use mapped timeframe for massive when checking cache
            cache_timeframe = timeframe
            if PROVIDER == 'massive':
                cache_timeframe = MASSIVE_TIMEFRAME_MAP.get(timeframe, timeframe)
            cached = fetcher.cache.load(symbol, PROVIDER, cache_timeframe, CACHE_FMT, date_range)
            if cached is not None:
                print(f"[CACHED] {symbol} {cache_timeframe} {date_range} already cached.")
                continue
            print(f"[CHECKING] {symbol} {cache_timeframe} {date_range} ...")
            df = None
            if PROVIDER == 'yfinance':
                interval = timeframe
                df = fetcher.fetch_yfinance(symbol, start, end, interval=interval)
            elif PROVIDER == 'massive':
                massive_timeframe = MASSIVE_TIMEFRAME_MAP.get(timeframe, timeframe)
                for attempt in range(1, MAX_RETRIES + 1):
                    try:
                        df = fetcher.fetch_massive(symbol, start, end, timeframe=massive_timeframe)
                        break
                    except Exception as e:
                        status_code = getattr(getattr(e, 'response', None), 'status_code', None)
                        if status_code == 429:
                            print(f"[Massive] 429 Too Many Requests for {symbol} ({cache_timeframe}). Attempt {attempt}/{MAX_RETRIES}. Retrying in {DELAY_SECONDS} seconds...")
                            time.sleep(DELAY_SECONDS)
                        else:
                            print(f"[Massive] Error for {symbol} ({cache_timeframe}): {e}")
                            break
                else:
                    print(f"[Massive] Failed to fetch {symbol} ({cache_timeframe}) after {MAX_RETRIES} retries due to rate limiting.")
            else:
                print(f"Unknown provider: {PROVIDER}")
                continue
            if df is not None and not df.empty:
                print(f"[OK] {symbol} {cache_timeframe} {date_range} fetched and cached. Rows: {len(df)}")
            else:
                print(f"[FAIL] {symbol} {cache_timeframe} {date_range} - No data.")

if __name__ == "__main__":
    main()
