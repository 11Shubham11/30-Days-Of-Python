"""Unit tests for scoring logic."""
from __future__ import annotations

import pandas as pd

from stock_scout.config import Filters, ScoringWeights
from stock_scout.scoring import compute_scores, rank_candidates


def sample_features() -> pd.DataFrame:
    data = {
        "symbol": ["AAA", "BBB", "CCC"],
        "momentum": [1.0, 0.5, 0.1],
        "volume_thrust": [0.9, 0.3, 0.2],
        "growth": [0.6, 0.4, 0.2],
        "catalyst": [1, 0, 2],
        "flow": [2, 0, 1],
        "sentiment": [0.5, -0.1, 0.0],
        "avg_turnover_inr": [5e7, 2e7, 4e7],
        "atr_pct": [0.05, 0.09, 0.04],
        "breakout_level": [100, 200, 150],
        "atr": [5, 8, 4],
        "sector": ["IT", "IT", "Finance"],
    }
    df = pd.DataFrame(data).set_index("symbol")
    return df


def test_compute_scores_shape() -> None:
    features = sample_features()
    scores = compute_scores(features, ScoringWeights())
    assert set(scores.columns) == {
        "momentum_score",
        "volume_score",
        "growth_score",
        "catalyst_score",
        "flow_score",
        "sentiment_score",
        "composite",
    }
    assert len(scores) == len(features)


def test_rank_candidates_respects_filters() -> None:
    features = sample_features()
    filters = Filters(min_turnover_inr=3e7, max_atr_pct=0.08, top_n=2, max_sector_exposure=1)
    result = rank_candidates(features, ScoringWeights(), filters)
    assert not result.top_candidates.empty
    assert (result.top_candidates["avg_turnover_inr"] >= filters.min_turnover_inr).all()
    assert (result.top_candidates["atr_pct"] <= filters.max_atr_pct + 1e-9).all()
    assert len(result.top_candidates) <= filters.top_n
    assert result.top_candidates["sector"].nunique() <= filters.max_sector_exposure
