# Stock Scout

`stock_scout` is a Python-based workflow designed to scan Indian equities each weekend, score them on momentum, growth, catalysts, flows, and sentiment, and publish a concise list of actionable trade ideas. The repository bundles ingestion blueprints for NSE-friendly data sources, a composite scoring engine, storage schema, and orchestration utilities so you can automate the entire weekly process.

## Highlights

- **Automated weekend runbook** that refreshes the trading universe, computes technical/fundamental signals, ranks candidates, and emits watchlists and alerts.
- **Modular ingestion layer** covering market data, corporate events, filings, flows, and news sentiment with clear boundaries for API scraping implementations.
- **Configurable scoring framework** implementing the composite weights outlined in the strategy description with normalization and liquidity/volatility filters.
- **Pluggable outputs** for Google Sheets, Slack/Telegram, and archival CSVs.
- **SQLite/Postgres ready** data model with tables for prices, indicators, events, filings, flows, news, and scoring snapshots.

## Repository Layout

```
stock_scout/
  __init__.py
  alerts.py
  config.py
  data_models.py
  pipeline.py
  scoring.py
  utils.py
  data_ingestion/
    __init__.py
    events.py
    flows.py
    market_data.py
    sentiment.py
config/
  settings.example.yaml
scripts/
  run_weekly.py
.env.example
README.md
requirements.txt
```

### Key Modules

- **`config.py`** – loads YAML configuration, environment variables, and runtime secrets (Twelve Data, Finnhub, Slack webhooks, etc.).
- **`data_ingestion`** – fetches OHLCV, indicators, corporate events, filings, bulk/block deals, and recent news. These modules include placeholders for API access and HTML parsing; implement them with the appropriate SDKs or scraping logic while respecting each provider’s terms of service.
- **`data_models.py`** – defines lightweight ORM models (SQLAlchemy) and helper factories for SQLite/Postgres deployments.
- **`scoring.py`** – computes the momentum/volume/growth/catalyst/flow/sentiment sub-scores, normalizes features, and aggregates them into a composite score.
- **`pipeline.py`** – orchestrates the full weekend cadence: refresh universe, pull datasets, engineer features, rank candidates, and generate trade plans.
- **`alerts.py`** – publishes the shortlisted ideas to Slack/Telegram and updates a Google Sheet watchlist.
- **`scripts/run_weekly.py`** – CLI entry point that executes the Saturday schedule (with optional weekday monitoring hooks).

## Getting Started

1. **Create a virtual environment** and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Copy the sample configuration** and fill in API keys / project settings:

   ```bash
   cp config/settings.example.yaml config/settings.yaml
   cp .env.example .env
   ```

   - `config/settings.yaml` holds scoring weights, liquidity filters, scheduling options, storage DSN, and output destinations.
   - `.env` should contain API tokens (Twelve Data, Finnhub), database credentials, and webhook URLs.

3. **Initialize the database schema** (SQLite by default):

   ```bash
   python -m stock_scout.data_models --init-db
   ```

4. **Run the weekend pipeline**:

   ```bash
   python scripts/run_weekly.py --config config/settings.yaml
   ```

   The script will refresh market data, compute scores, and push the top candidates to the configured outputs. Dry-run mode is available for development.

5. **Schedule automation** using cron, systemd timers, or Airflow. Example crontab entry (server set to IST):

   ```cron
   0 7 * * 6 cd /path/to/repo && .venv/bin/python scripts/run_weekly.py --config config/settings.yaml
   ```

## Compliance Notice

Ensure you follow the terms of service and licensing requirements for NSE/BSE websites, Twelve Data, Finnhub, Moneycontrol, and any other data providers. Consider purchasing licensed market data if you commercialize or scale usage.

## Backtesting & Research

The scaffolding is compatible with `vectorbt`, `backtrader`, or any pandas-based backtesting framework. Add historical runs to validate edge, measure drawdowns, and calibrate scoring thresholds before trading live capital.

## Contributing

- Add new data adapters under `stock_scout/data_ingestion`.
- Extend `scoring.py` with sector rotation or delivery volume factors.
- Wire additional outputs (Notion, email digests, dashboards).

## License

MIT License. See `LICENSE` (add your preferred terms).
