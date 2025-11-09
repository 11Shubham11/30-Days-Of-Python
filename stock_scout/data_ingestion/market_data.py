"""Market data ingestion via Twelve Data / Finnhub."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, List

import pandas as pd

from ..utils import http_get


@dataclass
class MarketData:
    """Collection of OHLCV candles and derived indicators."""

    prices: pd.DataFrame
    indicators: pd.DataFrame


def fetch_universe(api_key: str, exchange: str = "XNSE") -> pd.DataFrame:
    """Retrieve the tradable universe from Twelve Data."""

    url = "https://api.twelvedata.com/stocks"
    params = {"country": "India", "exchange": exchange, "format": "JSON", "source": "docs"}
    payload = http_get(url, params=params, headers={"Authorization": f"apikey {api_key}"})
    df = pd.DataFrame(payload.get("data", []))
    if not df.empty:
        df = df.rename(columns={"symbol": "symbol", "name": "name", "sector": "sector"})
    return df[["symbol", "name", "sector"]]


def fetch_ohlcv(symbols: Iterable[str], api_key: str, lookback_days: int = 400) -> pd.DataFrame:
    """Download OHLCV data for the given symbols."""

    end = datetime.utcnow()
    start = end - timedelta(days=lookback_days)
    frames: List[pd.DataFrame] = []
    for symbol in symbols:
        params = {
            "symbol": symbol,
            "interval": "1day",
            "start_date": start.strftime("%Y-%m-%d"),
            "end_date": end.strftime("%Y-%m-%d"),
            "apikey": api_key,
            "format": "JSON",
        }
        data = http_get("https://api.twelvedata.com/time_series", params=params)
        df = pd.DataFrame(data.get("values", []))
        if df.empty:
            continue
        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.rename(columns={
            "datetime": "date",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "volume": "volume",
        })
        df["symbol"] = symbol
        frames.append(df[["symbol", "date", "open", "high", "low", "close", "volume"]])
    if not frames:
        return pd.DataFrame(columns=["symbol", "date", "open", "high", "low", "close", "volume"])
    result = pd.concat(frames)
    result["date"] = pd.to_datetime(result["date"]).dt.date
    result = result.sort_values(["symbol", "date"])
    return result


def compute_indicators(prices: pd.DataFrame) -> pd.DataFrame:
    """Compute ATR, moving averages, Donchian breakouts, and RS metrics."""

    import pandas_ta as ta

    prices = prices.copy()
    prices["date"] = pd.to_datetime(prices["date"])

    def _calc(group: pd.DataFrame) -> pd.DataFrame:
        group = group.sort_values("date")
        group["atr"] = ta.atr(high=group["high"], low=group["low"], close=group["close"], length=14)
        group["ma21"] = ta.sma(group["close"], length=21)
        group["ma50"] = ta.sma(group["close"], length=50)
        group["ma200"] = ta.sma(group["close"], length=200)
        group["donchian20_high"] = ta.highest(group["high"], length=20)
        group["donchian55_high"] = ta.highest(group["high"], length=55)
        group["breakout_score"] = (group["close"] - group["donchian20_high"]) / group["donchian20_high"]
        group["volume_pct"] = group["volume"].rank(pct=True)
        return group

    enriched = prices.groupby("symbol", group_keys=False).apply(_calc)
    enriched["date"] = enriched["date"].dt.date
    indicators = enriched[[
        "symbol",
        "date",
        "atr",
        "ma21",
        "ma50",
        "ma200",
        "donchian20_high",
        "donchian55_high",
        "breakout_score",
        "volume_pct",
    ]].copy()
    indicators = indicators.rename(columns={"volume_pct": "vol_percentile"})
    return indicators


def fetch_market_data_with_indicators(symbols: Iterable[str], api_key: str) -> MarketData:
    prices = fetch_ohlcv(symbols, api_key=api_key)
    indicators = compute_indicators(prices) if not prices.empty else pd.DataFrame()
    return MarketData(prices=prices, indicators=indicators)
