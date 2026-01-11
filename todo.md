# TODO: Vectorized Stock Strategy Tester

## 1. Project Setup

- [ ] Set up Python 3.11.14 environment
- [ ] Install dependencies (vectorbt, Dash, yfinance, alpaca-py, polygon-api-client, pandas, numpy, plotly, python-dotenv, pytz)
- [ ] Configure .env for API keys
- [ ] Git

## 2. Data Layer

- [ ] Implement data fetchers for Massive (Polygon), Alpaca, yFinance
- [ ] Implement local caching (parquet/csv/feather)
- [ ] Ensure all data is timezone-aware (New York)

## 3. Strategy Layer

- [ ] Define strategy interface (Python, vectorbt, numpy)
- [ ] Create sample strategies

## 4. Backtesting Engine

- [ ] Build vectorized backtesting engine
- [ ] Support forward/backward testing with date ranges
- [ ] Integrate with cached data

## 5. Dashboard

- [ ] Set up Dash/Plotly dashboard
- [ ] Display standard trading metrics
- [ ] Add interactive charts and analysis

## 6. Paper Trading

- [ ] Integrate paper trading with Alpaca/Massive
- [ ] Enable live execution of successful strategies

## 7. Documentation & Extensibility

- [ ] Document architecture and usage
- [ ] Plan for future asset class support
