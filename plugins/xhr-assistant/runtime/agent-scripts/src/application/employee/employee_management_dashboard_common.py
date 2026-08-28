from __future__ import annotations

import asyncio
import re
from datetime import date
from typing import Any

from src.shared.http import fetch_json


MONTH_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
SNAKE_CASE_PART_PATTERN = re.compile(r"_([a-zA-Z0-9])")
MAX_CONCURRENT_REQUESTS = 6


def require_month(task_args: dict[str, Any]) -> str:
    month = str(task_args.get("month") or "").strip()
    if not MONTH_PATTERN.fullmatch(month):
        raise ValueError("month is required in YYYY-MM format")
    return month


def timeline_months(month: str) -> list[str]:
    current = date.fromisoformat(f"{month}-01")
    months = []
    for offset in range(5, -1, -1):
        year = current.year
        month_number = current.month - offset
        while month_number <= 0:
            year -= 1
            month_number += 12
        months.append(f"{year:04d}-{month_number:02d}")
    return months


def normalize_response_keys(value: Any) -> Any:
    if isinstance(value, list):
        return [normalize_response_keys(item) for item in value]
    if not isinstance(value, dict):
        return value
    return {
        SNAKE_CASE_PART_PATTERN.sub(
            lambda match: match.group(1).upper(), str(key)
        ): normalize_response_keys(item)
        for key, item in value.items()
    }


async def fetch_summary(client, url, headers, params):
    payload = await fetch_json(client, url, params=params, headers=headers)
    data = payload.get("data") if isinstance(payload, dict) else None
    if data is None:
        raise ValueError("Workforce report response is empty")
    return normalize_response_keys(data)


def report_request_key(params: dict[str, str]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted(params.items()))


async def fetch_summary_batch(client, url, headers, requests):
    """Fetch unique reports concurrently with section-safe result objects."""
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    unique_requests = {
        report_request_key(params): params for params in requests
    }

    async def fetch_one(key, params):
        async with semaphore:
            try:
                data = await fetch_summary(client, url, headers, params)
                return key, data, None
            except Exception:
                return key, None, "Workforce report data could not be loaded"

    results = await asyncio.gather(
        *(fetch_one(key, params) for key, params in unique_requests.items())
    )
    return {key: {"data": data, "error": error} for key, data, error in results}
