"""CLI entry point for running the Stock Scout pipeline."""
from __future__ import annotations

import argparse
from pathlib import Path

from stock_scout.config import load_settings
from stock_scout.pipeline import run_weekly_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Stock Scout weekly pipeline")
    parser.add_argument("--config", required=True, help="Path to settings YAML")
    parser.add_argument("--dry-run", action="store_true", help="Skip outbound alerts")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = load_settings(Path(args.config))
    if args.dry_run:
        settings.outputs = {}
    artifacts = run_weekly_pipeline(settings)
    print("Generated candidates:")
    print(artifacts.top_candidates.reset_index())


if __name__ == "__main__":
    main()
