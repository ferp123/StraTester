# TODO: Vectorized Stock Strategy Tester

## 1. Project Setup

- [ ] Set up Python 3.11.14 environment
- [ ] Install dependencies (vectorbt, Dash, yfinance, alpaca-py, polygon-api-client, pandas, numpy, plotly, python-dotenv, pytz)
- [x] Configure .env for API keys
- [x] Git

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

## 7. Error Handling & Logging

- [ ] Implement centralized error handling
- [ ] Set up logging with Python's logging module

## 8. Unit Testing

- [ ] Set up pytest and write unit tests
- [ ] Add integration tests for data and strategy layers

## 9. CI/CD

- [ ] Configure GitHub Actions for automated testing
- [ ] Add deployment workflow (optional)

## 10. Documentation & Extensibility

- [ ] Create docs/ directory and initial documentation
- [ ] Add docstrings and usage examples
- [ ] Plan for future asset class support
