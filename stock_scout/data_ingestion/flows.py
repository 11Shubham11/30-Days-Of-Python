"""Bulk/block deals ingestion."""
from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd


def fetch_bulk_block_deals(last_days: int = 5) -> pd.DataFrame:
    """Placeholder for NSE/BSE bulk-block deals scraping."""

    today = datetime.utcnow().date()
    data = [
        {
            "symbol": "ICICIBANK",
            "date": today - timedelta(days=2),
            "type": "bulk",
            "qty": 1_200_000,
            "avg_price": 960.5,
            "exchange": "NSE",
        }
    ]
    return pd.DataFrame(data)
