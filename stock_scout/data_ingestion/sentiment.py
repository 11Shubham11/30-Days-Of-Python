"""News sentiment ingestion via Finnhub."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable, List

import pandas as pd

from ..utils import http_get


def fetch_recent_news_with_sentiment(symbols: Iterable[str], api_key: str, last_days: int = 14) -> pd.DataFrame:
    """Fetch recent news headlines and compute naive sentiment scores."""

    end = datetime.utcnow().date()
    start = end - timedelta(days=last_days)
    frames: List[pd.DataFrame] = []
    for symbol in symbols:
        params = {
            "symbol": f"NSE:{symbol}",
            "from": start.isoformat(),
            "to": end.isoformat(),
            "token": api_key,
        }
        data = http_get("https://finnhub.io/api/v1/company-news", params=params)
        df = pd.DataFrame(data)
        if df.empty:
            continue
        df["symbol"] = symbol
        df["datetime"] = pd.to_datetime(df["datetime"], unit="s")
        df["sentiment"] = df["headline"].str.contains("wins|upbeat|growth|record", case=False).astype(int) - df[
            "headline"
        ].str.contains("loss|down|cuts|probe", case=False).astype(int)
        frames.append(df[["symbol", "datetime", "headline", "source", "sentiment"]])
    if not frames:
        return pd.DataFrame(columns=["symbol", "datetime", "headline", "source", "sentiment"])
    result = pd.concat(frames)
    result = result.rename(columns={"datetime": "date"})
    return result
