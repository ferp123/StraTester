# Vectorized Stock Strategy Tester: Project Plan

## Overview

A scalable, vectorized backtesting and paper trading system for stocks using Python 3.11.14, vectorbt, and Dash. The system fetches and caches data from Massive (Polygon), Alpaca, or yFinance, supports timezone-aware (New York) date handling, and provides a browser dashboard for analysis. Future expansion to other asset classes is considered.

## Architecture

- **Data Layer**: Modular fetchers for Massive, Alpaca, yFinance. Local cache (parquet/csv/feather).
- **Strategy Layer**: Python-based, vectorized (numpy/pandas/vectorbt) strategy definitions.
- **Backtesting Engine**: Runs strategies over cached data, supports forward/backward testing, timezone-aware.
- **Dashboard**: Dash/Plotly for metrics, charts, and analysis.
- **Paper Trading**: Live execution via broker APIs (Alpaca, Massive, etc.).

## Key Features

- Fast, vectorized computation (vectorbt, numpy, pandas)
- Modular data ingestion and caching
- Timezone-aware (New York standard)
- Browser-based dashboard (Dash/Plotly)
- Extensible for new asset classes and data sources
- Secure API key management via .env

## Milestones

1. Project setup, requirements, and environment
2. Data fetchers and caching
3. Strategy interface and sample strategies
4. Backtesting engine
5. Dashboard for results and metrics
6. Paper trading integration
7. Documentation and extensibility

## Future Expansion

- Support for crypto, forex, and other asset classes
- UI-based strategy builder
- Cloud deployment options
