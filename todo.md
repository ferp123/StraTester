# TODO: Vectorized Stock Strategy Tester

## 1. Project Setup

- [x] Set up Python 3.11.14 environment
- [x] Install dependencies (vectorbt, Dash, yfinance, alpaca-py, polygon-api-client, pandas, numpy, plotly, python-dotenv, pytz)
- [x] Configure .env for API keys
- [x] Git

## 2. Data Layer

- [x] Implement data fetchers for Massive (Polygon), Alpaca, yFinance
- [x] Implement local caching (parquet/csv/feather)
- [x] Ensure all data is timezone-aware (New York)

## 3. Strategy Layer

- [x] Define strategy interface (Python, vectorbt, numpy)
- [x] Create sample strategies
- [x] MACD Crossover strategy implemented and registered

## 4. Backtesting Engine

- [x] Build vectorized backtesting engine
- [x] Support forward/backward testing with date ranges
- [x] Integrate with cached data
- [x] Signal-based position holding and trade extraction logic validated

## 5. Dashboard

- [x] Set up Dash/Plotly dashboard
- [x] Display standard trading metrics
- [x] Add interactive charts and analysis
- [x] Dashboard extended for new strategies, custom CSS, and callback fixes
- [x] Cache file selection and robust error handling

## 6. Paper Trading

- [ ] Integrate paper trading with Alpaca/Massive
- [ ] Enable live execution of successful strategies

## 7. Error Handling & Logging

- [x] Implement centralized error handling in dashboard and data layer
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
