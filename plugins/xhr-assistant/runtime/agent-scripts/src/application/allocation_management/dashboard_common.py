from __future__ import annotations

import re
from datetime import date
from typing import Any

from src.shared.http import fetch_json


REPORT_FILTERS = (
    "departmentId",
    "employeeTypeId",
    "workLocationId",
    "jobTitleId",
    "sourceLineKey",
    "allocatedLineKey",
    "productLineId",
    "projectId",
    "employeeId",
)
MONTH_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
SNAKE_CASE_PART_PATTERN = re.compile(r"_([a-zA-Z0-9])")


def require_month(task_args: dict[str, Any], key: str) -> str:
    value = str(task_args.get(key) or "").strip()
    if not MONTH_PATTERN.fullmatch(value):
        raise ValueError(f"{key} is required in YYYY-MM format")
    return value


def build_filters(task_args: dict[str, Any]) -> dict[str, str]:
    return {
        key: str(task_args[key]).strip()
        for key in REPORT_FILTERS
        if task_args.get(key) is not None and str(task_args[key]).strip()
    }


def resolve_timeline_periods(task_args: dict[str, Any]) -> dict[str, Any]:
    month = require_month(task_args, "month")
    requested_timeline = task_args.get("timeline")
    has_range_argument = (
        task_args.get("fromMonth") is not None
        or task_args.get("toMonth") is not None
    )
    timeline = str(
        requested_timeline or ("RANGE" if has_range_argument else "MONTH")
    ).strip().upper()
    if timeline not in {"MONTH", "QUARTER", "YTD", "RANGE"}:
        raise ValueError("timeline must be MONTH, QUARTER, YTD, or RANGE")

    raw_from_month = task_args.get("fromMonth")
    raw_to_month = task_args.get("toMonth")
    if timeline == "RANGE":
        if raw_from_month is None or raw_to_month is None:
            raise ValueError("fromMonth and toMonth are required for RANGE")
        from_month = require_month(task_args, "fromMonth")
        to_month = require_month(task_args, "toMonth")
        if from_month > to_month:
            raise ValueError("fromMonth must be before or equal to toMonth")
        report_month = to_month
        summary_months = inclusive_months(from_month, to_month)
    elif timeline == "QUARTER":
        parsed = date.fromisoformat(f"{month}-01")
        quarter_start = ((parsed.month - 1) // 3) * 3 + 1
        summary_months = inclusive_months(
            f"{parsed.year:04d}-{quarter_start:02d}", month
        )
        report_month = month
    elif timeline == "YTD":
        summary_months = inclusive_months(f"{month[:4]}-01", month)
        report_month = month
    else:
        summary_months = [month]
        report_month = month

    trend_months = (
        previous_months(month, 3) if timeline == "MONTH" else summary_months
    )
    return {
        "timeline": timeline,
        "selectedMonth": month,
        "reportMonth": report_month,
        "summaryMonths": summary_months,
        "trendMonths": trend_months,
    }


def previous_months(month: str, count: int) -> list[str]:
    current = date.fromisoformat(f"{month}-01")
    months = []
    for offset in range(count - 1, -1, -1):
        year = current.year
        month_number = current.month - offset
        while month_number <= 0:
            year -= 1
            month_number += 12
        months.append(f"{year:04d}-{month_number:02d}")
    return months


def inclusive_months(from_month: str, to_month: str) -> list[str]:
    current = date.fromisoformat(f"{from_month}-01")
    end = date.fromisoformat(f"{to_month}-01")
    months = []
    while current <= end:
        months.append(current.strftime("%Y-%m"))
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)
    return months


async def fetch_dashboard_data(client, url, headers, params):
    payload = await fetch_json(client, url, params=params, headers=headers)

    data = payload.get("data") if isinstance(payload, dict) else None
    if data is None:
        raise ValueError("Dashboard response is empty")

    return normalize_response_keys(data)


def normalize_response_keys(value: Any) -> Any:
    """Mirror the frontend SDK's recursive snake_case to camelCase conversion."""
    if isinstance(value, list):
        return [normalize_response_keys(item) for item in value]
    if not isinstance(value, dict):
        return value

    normalized = {}
    for key, item in value.items():
        normalized_key = SNAKE_CASE_PART_PATTERN.sub(
            lambda match: match.group(1).upper(),
            str(key),
        )
        normalized[normalized_key] = normalize_response_keys(item)
    return normalized


def with_month(rows: Any, month: str) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        return []
    return [{"month": month, **row} for row in rows if isinstance(row, dict)]


def aggregate_breakdown_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    additive_keys = (
        "totalFte", "capacityManDays", "capacityManMonths", "allocatedManDays",
        "allocatedManMonths", "sourceFactCount",
    )
    grouped: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = str(row.get("id") or row.get("code") or row.get("key") or "")
        if key not in grouped:
            grouped[key] = {**row}
            continue
        for field in additive_keys:
            grouped[key][field] = (grouped[key].get(field) or 0) + (row.get(field) or 0)
    for row in grouped.values():
        capacity = row.get("capacityManMonths") or 0
        row["utilizationRate"] = (
            (row.get("allocatedManMonths") or 0) / capacity * 100
            if capacity > 0 else 0
        )
    return list(grouped.values())


def aggregate_rows(rows: list[dict[str, Any]], key_fields, additive_keys):
    grouped: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = ":".join(str(row.get(field) or "") for field in key_fields)
        if key not in grouped:
            grouped[key] = {**row}
            continue
        for field in additive_keys:
            grouped[key][field] = (grouped[key].get(field) or 0) + (row.get(field) or 0)
    return list(grouped.values())
