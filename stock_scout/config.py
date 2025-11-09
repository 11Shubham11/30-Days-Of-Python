"""Configuration helpers for Stock Scout."""
from __future__ import annotations

import dataclasses
import os
from pathlib import Path
from typing import Any, Mapping, Optional

import yaml
from dotenv import load_dotenv


@dataclasses.dataclass
class ApiKeys:
    """Container for external API keys."""

    twelve_data: str
    finnhub: str
    slack_webhook: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    google_service_account_json: Optional[Path] = None


@dataclasses.dataclass
class StorageConfig:
    """Database and storage backends."""

    database_url: str = "sqlite:///data/stock_scout.db"
    parquet_path: Path = Path("data/parquet")


@dataclasses.dataclass
class ScoringWeights:
    """Weights applied to each scoring component."""

    momentum: float = 0.35
    volume: float = 0.20
    growth: float = 0.15
    catalyst: float = 0.15
    flow: float = 0.10
    sentiment: float = 0.05


@dataclasses.dataclass
class Filters:
    """Liquidity and volatility filters."""

    min_turnover_inr: float = 30_000_000  # ₹3 crore
    max_atr_pct: float = 0.08
    max_sector_exposure: int = 3
    top_n: int = 10


@dataclasses.dataclass
class Schedule:
    """Cron-style schedule definitions."""

    weekend_run: str = "0 7 * * 6"
    intraday_watch: Optional[str] = None


@dataclasses.dataclass
class Settings:
    """Complete application settings."""

    api_keys: ApiKeys
    storage: StorageConfig = StorageConfig()
    scoring: ScoringWeights = ScoringWeights()
    filters: Filters = Filters()
    schedule: Schedule = Schedule()
    outputs: Mapping[str, Any] = dataclasses.field(default_factory=dict)


def load_settings(path: Path | str) -> Settings:
    """Load settings from YAML and environment variables."""

    load_dotenv()
    with open(path, "r", encoding="utf-8") as fh:
        raw_cfg = yaml.safe_load(fh) or {}

    env_api_keys = ApiKeys(
        twelve_data=os.getenv("TWELVE_DATA_API_KEY", ""),
        finnhub=os.getenv("FINNHUB_API_KEY", ""),
        slack_webhook=os.getenv("SLACK_WEBHOOK_URL"),
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID"),
        google_service_account_json=(
            Path(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))
            if os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
            else None
        ),
    )

    api_cfg = raw_cfg.get("api_keys", {})
    api_keys = dataclasses.replace(
        env_api_keys,
        twelve_data=api_cfg.get("twelve_data", env_api_keys.twelve_data),
        finnhub=api_cfg.get("finnhub", env_api_keys.finnhub),
        slack_webhook=api_cfg.get("slack_webhook", env_api_keys.slack_webhook),
        telegram_bot_token=api_cfg.get("telegram_bot_token", env_api_keys.telegram_bot_token),
        telegram_chat_id=api_cfg.get("telegram_chat_id", env_api_keys.telegram_chat_id),
    )

    storage_cfg = raw_cfg.get("storage", {})
    storage_defaults = StorageConfig()
    storage = StorageConfig(
        database_url=storage_cfg.get("database_url", storage_defaults.database_url),
        parquet_path=Path(storage_cfg.get("parquet_path", storage_defaults.parquet_path)),
    )

    scoring_cfg = raw_cfg.get("scoring", {})
    scoring_defaults = ScoringWeights()
    scoring = ScoringWeights(
        momentum=scoring_cfg.get("momentum", scoring_defaults.momentum),
        volume=scoring_cfg.get("volume", scoring_defaults.volume),
        growth=scoring_cfg.get("growth", scoring_defaults.growth),
        catalyst=scoring_cfg.get("catalyst", scoring_defaults.catalyst),
        flow=scoring_cfg.get("flow", scoring_defaults.flow),
        sentiment=scoring_cfg.get("sentiment", scoring_defaults.sentiment),
    )

    filters_cfg = raw_cfg.get("filters", {})
    filter_defaults = Filters()
    filters = Filters(
        min_turnover_inr=filters_cfg.get("min_turnover_inr", filter_defaults.min_turnover_inr),
        max_atr_pct=filters_cfg.get("max_atr_pct", filter_defaults.max_atr_pct),
        max_sector_exposure=filters_cfg.get("max_sector_exposure", filter_defaults.max_sector_exposure),
        top_n=filters_cfg.get("top_n", filter_defaults.top_n),
    )

    schedule_cfg = raw_cfg.get("schedule", {})
    schedule_defaults = Schedule()
    schedule = Schedule(
        weekend_run=schedule_cfg.get("weekend_run", schedule_defaults.weekend_run),
        intraday_watch=schedule_cfg.get("intraday_watch", schedule_defaults.intraday_watch),
    )

    return Settings(
        api_keys=api_keys,
        storage=storage,
        scoring=scoring,
        filters=filters,
        schedule=schedule,
        outputs=raw_cfg.get("outputs", {}),
    )


__all__ = [
    "ApiKeys",
    "Filters",
    "ScoringWeights",
    "Schedule",
    "Settings",
    "StorageConfig",
    "load_settings",
]
