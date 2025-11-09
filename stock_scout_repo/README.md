# Stock Scout Weekly Strategy

This repository documents the complete workflow for a weekly NSE equity screening agent. The agent ingests market, corporate, flow, and sentiment data every weekend, computes composite scores, and surfaces the top trade candidates along with trade plans and alerts.

## 1. Weekly Operating Summary
- **Weekend cadence (Saturday/Sunday, IST)**
  - Refresh the tradable universe and price/volume history.
  - Pull near-term events, corporate filings, corporate actions, and deal flows.
  - Score all liquid stocks on growth, momentum, catalysts, flows, and sentiment.
  - Produce 5–10 high-conviction candidates with entries, stops, targets, and risk notes.
  - Log all outputs and auto-build a watchlist to monitor intraday breakouts during the week.
- **Weekday cadence (Mon–Fri, 09:15–15:30 IST)**
  - Light monitoring for breakout alerts—no continuous polling.

## 2. Signal Library
### A. Momentum & Trend
- 12/26-week relative strength versus NIFTY50 and NIFTY500.
- 20/55-day Donchian breakout strength and distance from consolidation highs.
- Moving-average stack: `Close > 21DMA > 50DMA > 200DMA`.
- Volume thrust: 20-day volume percentile and 2–3× spike on breakout day.

### B. Growth & Quality
- Trailing YoY revenue/EBITDA growth and margin trend (last 4–8 quarters).
- Positive earnings revision proximity via guidance/filings.

### C. Catalyst Proximity
- Events within ±10 trading days: results, board meetings, splits/bonuses, demergers, fundraising announcements.

### D. Flow
- Bulk/block deals during the past 5 trading days and net institutional participation.

### E. Sentiment
- News tone over the last 7–14 days with strong positive cluster flags.

## 3. Composite Scoring Framework
`Composite = 0.35*Momentum + 0.20*Volume + 0.15*Growth + 0.15*Catalyst + 0.10*Flow + 0.05*Sentiment`
- Normalize sub-scores to 0–100 with outlier winsorization.
- Penalize illiquid names (avg turnover < ₹3–5 cr) and high gap risk (ATR% > 6–8%).

## 4. Trade Plan Logic
- **Entry:** Breakout or first pullback to breakout zone with volume ≥ 1.5× 20-day average.
- **Initial stop:** 1.0–1.25× ATR(14) below entry or just under the base low.
- **Targets:** `T1 = entry + 1×ATR`, `T2 = entry + 2×ATR`; trail to prior swing low or 10-EMA after T1.

## 5. Weekly Schedule (IST)
| Time | Task |
|------|------|
| 07:00 Sat | Refresh universe, OHLCV, indicators |
| 07:30 Sat | Pull next two weeks of events |
| 07:40 Sat | Pull filings from the last 7 days |
| 07:50 Sat | Pull bulk/block deals from last 5 days |
| 08:00 Sat | Pull news headlines and score sentiment |
| 08:05 Sat | Compute signals and shortlist Top 20 |
| 08:10 Sat | Apply liquidity/ATR filters, sector caps, pick Top 5–10 |
| 08:15 Sat | Generate thesis, entry, stop, targets, risk tag per candidate |
| Mon–Fri | Monitor breakout alerts only |

## 6. Tech Stack & Architecture
- **Ingestion/compute:** Python (pandas, numpy, requests/httpx).
- **Indicators:** TA-Lib or pandas-ta for ATR, Donchian, relative strength.
- **Backtesting:** backtrader or vectorbt for score validation.
- **Storage:** SQLite/Postgres plus Parquet for price history.
- **Orchestration:** cron/Airflow or AWS Lambda.
- **Alerts/outputs:** Slack/Telegram and Google Sheets or Notion; optional Streamlit dashboard.

### APIs & Data Sources
- Twelve Data for NSE symbols, OHLCV, indicators.
- Finnhub for fundamentals and news sentiment.
- NSE India for corporate filings, events, corporate actions, bulk/block archives.
- Moneycontrol results calendar as backup.
- NSE historical reports for validation.
- Ensure compliance with NSE/BSE terms and licensing.

## 7. Minimal Data Model
```
symbols(symbol, name, sector, is_active)
prices(symbol, date, o, h, l, c, v)
indicators(symbol, date, atr, rsi, ma21, ma50, ma200, breakout_score, vol_percentile, rs_nifty)
events(symbol, date, type, note)
filings(symbol, date, headline, url)
flows(symbol, date, type, qty, avg_price, exchange)
news(symbol, date, headline, source, sentiment)
scores(symbol, asof, composite, notes, entry, sl, t1, t2)
```
- Index `(symbol, date)` for speed.

## 8. Pseudocode Blueprint
```python
# 0) Universe
symbols = get_symbols_from_twelve_data(exchange="XNSE")

# 1) Market data
prices = fetch_ohlcv(symbols, lookback_days=400)
ind = calc_indicators(prices)

# 2) Events/filings/corporate actions
events  = scrape_nse_events(next_days=14)
filings = scrape_nse_filings(last_days=7)
actions = scrape_nse_corp_actions(last_days=30)

# 3) Flows
deals = fetch_bulk_block(last_days=5)

# 4) Sentiment
news  = finnhub_market_news(symbols, last_days=14)
news["sentiment"] = score_news(news)

# 5) Feature assembly
X = make_features(ind, events, filings, actions, deals, news)

# 6) Scoring
scores = (0.35*X["momentum"] + 0.20*X["volume_thrust"] + 0.15*X["growth"] +
          0.15*X["catalyst"] + 0.10*X["flow"] + 0.05*X["sentiment"])

candidates = filter_liquidity_and_risk(X, min_turnover=3e7, max_atr_pct=0.08)
top = rank_and_pick(candidates, scores, top_n=10, sector_cap=3)

# 7) Trade plan
for s in top:
    entry = pick_entry(s)
    sl    = entry - 1.1 * ATR(s)
    t1, t2 = entry + 1 * ATR(s), entry + 2 * ATR(s)
    write_note(s, entry, sl, t1, t2, why=s.top_features)

# 8) Output & alerts
push_to_gsheet(top)
send_slack_digest(top)
```

## 9. Risk Management for ₹1 Lakh Portfolio
- Risk 1.5–2.0% of capital per trade.
- Position size = `risk_per_trade / (entry - stop)`, cap each position at ₹20–30k.
- Hold max 3–4 concurrent positions; raise cash when volatility spikes.
- Maintain hard stops, exit gap-downs immediately, trail stops post-T1.

## 10. Backtesting Checklist
- Universe: NIFTY500 over 4–6 years.
- Rebalance weekly; entries fire on next trading day open once triggered.
- Include brokerage, STT, slippage (0.10–0.20%).
- Track CAGR, max drawdown, win rate, avg win/loss, profit factor, exposure time.
- Perform annual walk-forward reweighting.

## 11. Deployment Recipe
- Package as `stock_scout` Python project.
- YAML config for thresholds (ATR cap, turnover floor, weights).
- `.env` for API keys.
- Scheduler: cron or Lambda (Sat 07:00 weekly + weekday 09:20 alerts).
- Outputs: Google Sheet "Weekly Picks", Slack digest, CSV archive.

## 12. Optional Enhancements
- Sector rotation overlays favoring outperforming sectors.
- Delivery percentage trends alongside price.
- Post-earnings pullback playbook (buy retest of 10-EMA).
- Regulatory/macro flag tracking for context.
