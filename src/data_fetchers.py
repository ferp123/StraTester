import pytz


import os
from dotenv import load_dotenv
import pandas as pd
import yfinance as yf
from typing import Optional
import sys
import argparse
try:
    from .cache import DataCache
except ImportError:
    from cache import DataCache
from polygon import RESTClient as PolygonClient
from datetime import datetime, timedelta


class DataFetcher:
    def __init__(self, cache_fmt: str = 'parquet'):
        load_dotenv()
        self.massive_api_key = os.getenv("MASSIVE_API_KEY")
        self.polygon_api_key = os.getenv("POLYGON_API_KEY")
        self.cache = DataCache()
        self.cache_fmt = cache_fmt


    def fetch_yfinance(self, symbol: str, start: str, end: str, interval: str = "1d") -> Optional[pd.DataFrame]:
        provider = 'yfinance'
        timeframe = interval
        date_range = f"{start}_to_{end}"
        # yFinance 1m limitation: only fetch last 7 days
        if interval == '1m':
            max_start = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d')
            if start < max_start:
                print(f"[SKIP] {symbol} 1m {start} to {end}: yFinance only allows 1m data for the last 7 days.")
                return None
        cached = self.cache.load(symbol, provider, timeframe, self.cache_fmt, date_range)
        if cached is not None:
            return cached
        try:
            df = yf.download(symbol, start=start, end=end, interval=interval, auto_adjust=True)
            if df is not None and not df.empty:
                # Localize index to US/Eastern
                eastern = pytz.timezone('America/New_York')
                # Ensure index is a DatetimeIndex
                if not isinstance(df.index, pd.DatetimeIndex):
                    df.index = pd.to_datetime(df.index)
                if df.index.tz is None or df.index.tz is pd.NaT:
                    df.index = df.index.tz_localize('UTC').tz_convert(eastern)
                else:
                    df.index = df.index.tz_convert(eastern)
                df.index.name = "datetime"
                self.cache.save(df, symbol, provider, timeframe, self.cache_fmt, date_range)
                return df
            else:
                print(f"yFinance: No data returned for {symbol} from {start} to {end} (interval={interval}). Columns: {df.columns if df is not None else 'None'}")
                if df is not None:
                    print(f"yFinance: DataFrame shape: {df.shape}, head: {df.head()}.")
                return None
        except Exception as e:
            print(f"yFinance: Exception occurred for {symbol} from {start} to {end} (interval={interval}): {e}")
            return None

    def fetch_massive(self, symbol: str, start: str, end: str, timeframe: str = "day") -> Optional[pd.DataFrame]:
        provider = 'massive'
        # Map timeframe for massive
        tf_map = {'1d': 'day', '1min': 'minute', '1m': 'minute', '5min': 'minute', '1h': 'hour'}
        mapped_timeframe = tf_map.get(timeframe, timeframe)
        date_range = f"{start}_to_{end}"
        cache_path = self.cache._get_path(symbol, provider, mapped_timeframe, self.cache_fmt, date_range)
        cached = self.cache.load(symbol, provider, mapped_timeframe, self.cache_fmt, date_range)
        if cached is not None:
            print(f"[CACHE] Data already exists in {cache_path}")
            return cached
        if not self.polygon_api_key:
            raise ValueError("Polygon API key not set in environment.")
        client = PolygonClient(self.polygon_api_key)
        start_dt = pd.to_datetime(start).strftime('%Y-%m-%d')
        end_dt = pd.to_datetime(end).strftime('%Y-%m-%d')
        bars = client.get_aggs(symbol, 1, mapped_timeframe, start_dt, end_dt)
        df = pd.DataFrame([bar.__dict__ for bar in bars])
        if not df.empty:
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('datetime', inplace=True)
            self.cache.save(df, symbol, provider, mapped_timeframe, self.cache_fmt, date_range)
            return df
        else:
            print(f"Massive: No data returned for {symbol} from {start} to {end} (timeframe={mapped_timeframe}).")
            return None
def parse_period(period_str):
    import re
    match = re.match(r"(\d+)(day|d|minute|min|m)", period_str.lower())
    if not match:
        raise ValueError(f"Invalid period format: {period_str}")
    num, unit = match.groups()
    num = int(num)
    if unit in ["day", "d"]:
        return num, "day"
    elif unit in ["minute", "min", "m"]:
        return num, "minute"
    else:
        raise ValueError(f"Unsupported period unit: {unit}")

def main():
    parser = argparse.ArgumentParser(description="Fetch market data and cache it.")
    parser.add_argument("-provider", choices=["massive", "yfinance"], required=True, help="Data provider to use.")
    parser.add_argument("-period", required=True, help="Period to fetch, e.g. 30day, 60min.")
    parser.add_argument("-symbol", required=True, help="Ticker symbol, e.g. AAPL, GOOGL.")
    args = parser.parse_args()

    num, unit = parse_period(args.period)
    end = datetime.today().strftime('%Y-%m-%d')
    start = (datetime.today() - timedelta(days=num if unit == "day" else 0, minutes=num if unit == "minute" else 0)).strftime('%Y-%m-%d')

    fetcher = DataFetcher(cache_fmt='parquet')
    symbol = args.symbol

    if args.provider == "yfinance":
        interval = "1d" if unit == "day" else "1m"
        df = fetcher.fetch_yfinance(symbol, start, end, interval=interval)
    elif args.provider == "massive":
        timeframe = "day" if unit == "day" else "minute"
        df = fetcher.fetch_massive(symbol, start, end, timeframe=timeframe)
    else:
        print(f"Unknown provider: {args.provider}")
        sys.exit(1)

    if df is not None:
        print(f"Fetched {len(df)} rows for {symbol} from {args.provider}.")
        print(df.head())
    else:
        print(f"No data fetched for {symbol} from {args.provider}.")

if __name__ == "__main__":
    main()




    def fetch_massive(self, symbol: str, start: str, end: str, timeframe: str = "day") -> Optional[pd.DataFrame]:
        provider = 'massive'
        cached = self.cache.load(symbol, provider, self.cache_fmt)
        if cached is not None:
            return cached
        if not self.polygon_api_key:
            raise ValueError("Polygon API key not set in environment.")
        client = PolygonClient(self.polygon_api_key)
        start_dt = pd.to_datetime(start).strftime('%Y-%m-%d')
        end_dt = pd.to_datetime(end).strftime('%Y-%m-%d')
        bars = client.get_aggs(symbol, 1, timeframe, start_dt, end_dt)
        df = pd.DataFrame([bar.__dict__ for bar in bars])
        if not df.empty:
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('datetime', inplace=True)
            self.cache.save(df, symbol, provider, self.cache_fmt)
            return df
        else:
            print(f"Massive: No data returned for {symbol} from {start} to {end} (timeframe={timeframe}).")
            return None


