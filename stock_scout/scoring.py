"""Scoring utilities for Stock Scout."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np
import pandas as pd

from .config import Filters, ScoringWeights


@dataclass
class ScoreResult:
    """Composite scoring output."""

    scores: pd.DataFrame
    top_candidates: pd.DataFrame


def _normalize(series: pd.Series) -> pd.Series:
    if series.empty:
        return series
    winsorized = series.clip(lower=series.quantile(0.05), upper=series.quantile(0.95))
    min_val, max_val = winsorized.min(), winsorized.max()
    if np.isclose(max_val, min_val):
        return pd.Series(50.0, index=series.index)
    scaled = 100 * (winsorized - min_val) / (max_val - min_val)
    return scaled.fillna(0.0)


def compute_scores(features: pd.DataFrame, weights: ScoringWeights) -> pd.DataFrame:
    """Compute component scores and the composite value."""

    components = {
        "momentum_score": _normalize(features["momentum"]),
        "volume_score": _normalize(features["volume_thrust"]),
        "growth_score": _normalize(features["growth"]),
        "catalyst_score": _normalize(features["catalyst"]),
        "flow_score": _normalize(features["flow"]),
        "sentiment_score": _normalize(features["sentiment"]),
    }
    comp_df = pd.DataFrame(components, index=features.index)
    comp_df["composite"] = (
        weights.momentum * comp_df["momentum_score"]
        + weights.volume * comp_df["volume_score"]
        + weights.growth * comp_df["growth_score"]
        + weights.catalyst * comp_df["catalyst_score"]
        + weights.flow * comp_df["flow_score"]
        + weights.sentiment * comp_df["sentiment_score"]
    )
    return comp_df


def apply_filters(
    scores: pd.DataFrame,
    features: pd.DataFrame,
    filters: Filters,
    sector_column: str = "sector",
) -> pd.DataFrame:
    """Filter by liquidity, volatility, and sector concentration."""

    mask = (features["avg_turnover_inr"] >= filters.min_turnover_inr) & (
        features["atr_pct"] <= filters.max_atr_pct
    )
    filtered = scores.loc[mask].copy()
    filtered[sector_column] = features.loc[mask, sector_column]
    filtered = filtered.sort_values("composite", ascending=False)

    counts: Dict[str, int] = {}
    keep_indices = []
    for idx, row in filtered.iterrows():
        sector = row.get(sector_column, "Unknown")
        counts.setdefault(sector, 0)
        if counts[sector] >= filters.max_sector_exposure:
            continue
        counts[sector] += 1
        keep_indices.append(idx)
        if len(keep_indices) >= filters.top_n:
            break
    return filtered.loc[keep_indices]


def attach_trade_plan(candidates: pd.DataFrame, features: pd.DataFrame) -> pd.DataFrame:
    """Generate entry/stop/target levels based on ATR."""

    enriched = candidates.join(
        features[[
            "breakout_level",
            "atr",
            "avg_turnover_inr",
            "atr_pct",
        ]],
        how="left",
    )
    enriched = enriched.rename(columns={"breakout_level": "entry"})
    enriched["stop_loss"] = enriched["entry"] - 1.1 * enriched["atr"]
    enriched["target1"] = enriched["entry"] + 1.0 * enriched["atr"]
    enriched["target2"] = enriched["entry"] + 2.0 * enriched["atr"]
    return enriched


def rank_candidates(features: pd.DataFrame, weights: ScoringWeights, filters: Filters) -> ScoreResult:
    scores = compute_scores(features, weights)
    filtered = apply_filters(scores, features, filters)
    trade_plan = attach_trade_plan(filtered, features)
    return ScoreResult(scores=scores, top_candidates=trade_plan)


__all__ = ["ScoreResult", "apply_filters", "compute_scores", "rank_candidates"]
