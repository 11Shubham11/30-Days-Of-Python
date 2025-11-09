"""SQLAlchemy models defining the Stock Scout schema."""
from __future__ import annotations

import argparse
from datetime import datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
)
from sqlalchemy.orm import registry

DEFAULT_METADATA = MetaData()
mapper_registry = registry(metadata=DEFAULT_METADATA)


def _table(name: str, *columns: Column) -> Table:
    return Table(name, DEFAULT_METADATA, *columns)


symbols = _table(
    "symbols",
    Column("symbol", String(32), primary_key=True),
    Column("name", String(128), nullable=False),
    Column("sector", String(64)),
    Column("is_active", Integer, default=1),
)

prices = _table(
    "prices",
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("symbol", String(32), ForeignKey("symbols.symbol")),
    Column("date", Date, index=True),
    Column("open", Float),
    Column("high", Float),
    Column("low", Float),
    Column("close", Float),
    Column("volume", Float),
)

indicators = _table(
    "indicators",
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("symbol", String(32), ForeignKey("symbols.symbol")),
    Column("date", Date, index=True),
    Column("atr", Float),
    Column("rsi", Float),
    Column("ma21", Float),
    Column("ma50", Float),
    Column("ma200", Float),
    Column("breakout_score", Float),
    Column("vol_percentile", Float),
    Column("rs_nifty", Float),
)

events = _table(
    "events",
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("symbol", String(32), ForeignKey("symbols.symbol")),
    Column("date", Date, index=True),
    Column("type", String(32)),
    Column("note", String(512)),
)

filings = _table(
    "filings",
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("symbol", String(32), ForeignKey("symbols.symbol")),
    Column("date", Date, index=True),
    Column("headline", String(512)),
    Column("url", String(512)),
)

flows = _table(
    "flows",
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("symbol", String(32), ForeignKey("symbols.symbol")),
    Column("date", Date, index=True),
    Column("type", String(32)),
    Column("qty", Float),
    Column("avg_price", Float),
    Column("exchange", String(8)),
)

news = _table(
    "news",
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("symbol", String(32), ForeignKey("symbols.symbol")),
    Column("date", DateTime, default=datetime.utcnow, index=True),
    Column("headline", String(512)),
    Column("source", String(64)),
    Column("sentiment", Float),
)

scores = _table(
    "scores",
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("symbol", String(32), ForeignKey("symbols.symbol"), index=True),
    Column("asof", Date, index=True),
    Column("composite", Float),
    Column("entry", Float),
    Column("stop_loss", Float),
    Column("target1", Float),
    Column("target2", Float),
    Column("notes", String(512)),
)


def init_db(database_url: str) -> None:
    """Create all tables on the configured database."""

    engine = create_engine(database_url)
    DEFAULT_METADATA.create_all(engine)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize Stock Scout database tables")
    parser.add_argument("--database-url", default="sqlite:///data/stock_scout.db")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    init_db(args.database_url)
    print(f"Initialized database at {args.database_url}")


if __name__ == "__main__":
    main()
