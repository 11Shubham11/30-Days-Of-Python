"""Corporate events and filings ingestion."""
from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd


def fetch_corporate_events(next_days: int = 14) -> pd.DataFrame:
    """Placeholder for NSE corporate events scraping."""

    today = datetime.utcnow().date()
    data = [
        {
            "symbol": "INFY",
            "date": today + timedelta(days=5),
            "type": "earnings",
            "note": "Q2 FY24 results",
        }
    ]
    return pd.DataFrame(data)


def fetch_recent_filings(last_days: int = 7) -> pd.DataFrame:
    """Placeholder for NSE filings scraping."""

    today = datetime.utcnow().date()
    data = [
        {
            "symbol": "RELIANCE",
            "date": today - timedelta(days=1),
            "headline": "Reliance announces new retail JV",
            "url": "https://www.nseindia.com/filings/...",
        }
    ]
    return pd.DataFrame(data)


def fetch_recent_corporate_actions(last_days: int = 30) -> pd.DataFrame:
    """Placeholder for corporate actions data."""

    today = datetime.utcnow().date()
    data = [
        {
            "symbol": "TCS",
            "date": today + timedelta(days=8),
            "type": "dividend",
            "note": "Interim dividend record date",
        }
    ]
    return pd.DataFrame(data)
