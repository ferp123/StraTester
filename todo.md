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

# 11. Save button

        1. What to Save
            Backtest settings: Symbol, provider, strategy, parameters, capital, risk, slippage, commission, cache file, date/time, etc.
            Performance metrics: All metrics shown in the dashboard (final equity, return, drawdown, win rate, etc.).
            Trade log: The full trade list for the run.
            Optional: Equity curve, price/signals, or even the full backtest data (could be large).
        2. Where to Save
            Local file (CSV/JSON): Save each run as a file in a dedicated folder (e.g., saved_runs/). JSON is flexible for settings + metrics; CSV is good for trade logs.
            Database: For more advanced use, runs could be stored in SQLite or another DB for easy querying and comparison.
            In-app memory: For quick access during the session, but not persistent.
        3. How to Trigger
            Dashboard button: Add a “Save Run” button to the dashboard UI.
            Auto-save: Optionally, auto-save every run, or prompt the user after each run.
        4. How to Load/View
            Saved runs list: Add a dropdown or table to view/load previous runs.
            Comparison: Allow comparing saved runs side by side.
        5. Implementation Suggestion (MVP)
            Add a “Save Run” button to the dashboard.
            When clicked, save a JSON file in a saved_runs/ folder with:
            All backtest settings
            All performance metrics
            Trade log (as a list of dicts)
            Timestamp and unique ID
            Optionally, add a “Saved Runs” section to view/load previous runs.
