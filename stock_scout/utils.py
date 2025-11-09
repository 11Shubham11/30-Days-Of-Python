"""Utility helpers."""
from __future__ import annotations

import logging
from typing import Any, Dict, Mapping, Optional

import httpx

logger = logging.getLogger(__name__)


class StockScoutError(RuntimeError):
    """Base error for the package."""


def http_get(url: str, params: Optional[Mapping[str, Any]] = None, headers: Optional[Mapping[str, str]] = None) -> Dict[str, Any]:
    """HTTP GET helper with structured errors."""

    try:
        response = httpx.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        if "application/json" in response.headers.get("Content-Type", ""):
            return response.json()
        return {"raw": response.text}
    except httpx.HTTPError as exc:
        logger.error("HTTP GET failed", exc_info=exc)
        raise StockScoutError(f"Failed to fetch {url}: {exc}") from exc
