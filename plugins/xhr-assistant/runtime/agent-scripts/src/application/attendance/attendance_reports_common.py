from __future__ import annotations

import calendar
import re
from datetime import date, datetime, timedelta, timezone
from typing import Any

from src.shared.http import fetch_json


MONTH_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
DATE_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")
SNAKE_CASE_PART_PATTERN = re.compile(r"_([a-zA-Z0-9])")

VALID_MODES = {"month", "week", "annual"}
VALID_STATUSES = {"APPROVED", "PENDING"}


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


def to_total_minutes(duration: dict[str, Any] | None) -> int:
    if not isinstance(duration, dict):
        return 0
    hours = duration.get("hours") or 0
    minutes = duration.get("minutes") or 0
    try:
        return int(hours) * 60 + int(minutes)
    except (ValueError, TypeError):
        return 0


def format_duration(duration: dict[str, Any] | int | None) -> str:
    if isinstance(duration, dict):
        total_mins = to_total_minutes(duration)
    elif isinstance(duration, (int, float)):
        total_mins = int(duration)
    else:
        return "0h"

    if total_mins == 0:
        return "0h"
    hours = total_mins // 60
    minutes = total_mins % 60
    if hours > 0 and minutes > 0:
        return f"{hours}h {minutes:02d}m"
    if hours > 0:
        return f"{hours}h"
    return f"{minutes}m"


def format_signed_minutes(minutes: int | None) -> str:
    safe_minutes = minutes or 0
    if safe_minutes == 0:
        return "0h"
    sign = "+" if safe_minutes > 0 else "-"
    absolute_minutes = abs(safe_minutes)
    hours = absolute_minutes // 60
    minute_remainder = absolute_minutes % 60

    hour_display = f"{hours}h" if hours > 0 else ""
    minute_display = (
        f"{minute_remainder:02d}m" if hours > 0 and minute_remainder > 0
        else f"{minute_remainder}m" if minute_remainder > 0
        else ""
    )
    parts = [p for p in (hour_display, minute_display) if p]
    return f"{sign}{' '.join(parts)}" if parts else "0h"


def get_regular_overtime_balance_minutes(
    balance_minutes: int | None,
    rest_day_overtime: dict[str, Any] | None,
    public_holiday_overtime: dict[str, Any] | None,
) -> int:
    safe_balance = balance_minutes or 0
    rest_day_mins = to_total_minutes(rest_day_overtime)
    holiday_mins = to_total_minutes(public_holiday_overtime)
    return safe_balance - rest_day_mins - holiday_mins


def get_report_overtime_display_minutes(
    report_entry: dict[str, Any], status: str
) -> int:
    balance_minutes = report_entry.get("balanceMinutes")
    overtime_hours = report_entry.get("overtimeHours")
    if status == "PENDING":
        if overtime_hours is not None:
            return to_total_minutes(overtime_hours)
        return balance_minutes or 0
    if balance_minutes is not None:
        return balance_minutes
    if overtime_hours is not None:
        return to_total_minutes(overtime_hours)
    return 0


def resolve_report_period(task_args: dict[str, Any]) -> dict[str, Any]:
    mode = str(task_args.get("mode") or "month").strip().lower()
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be one of: {', '.join(sorted(VALID_MODES))}")

    status = str(task_args.get("status") or "APPROVED").strip().upper()
    if status not in VALID_STATUSES:
        raise ValueError(f"status must be one of: {', '.join(sorted(VALID_STATUSES))}")

    today = datetime.now(timezone.utc).date()

    if mode == "annual":
        year_raw = task_args.get("year")
        if year_raw is not None and str(year_raw).strip():
            try:
                year = int(year_raw)
            except (ValueError, TypeError):
                raise ValueError("year must be a valid integer (e.g. 2026)")
        else:
            year = today.year
        return {
            "mode": "annual",
            "status": "APPROVED",  # Annual reports represent approved facts only
            "year": year,
            "startDate": f"{year}-01-01",
            "endDate": f"{year}-12-31",
        }

    if mode == "week":
        start_date = str(task_args.get("startDate") or task_args.get("start_date") or "").strip()
        end_date = str(task_args.get("endDate") or task_args.get("end_date") or "").strip()
        if start_date and end_date:
            if not DATE_PATTERN.fullmatch(start_date) or not DATE_PATTERN.fullmatch(end_date):
                raise ValueError("startDate and endDate must be in YYYY-MM-DD format")
        else:
            # Default to current week (Monday to Sunday)
            weekday = today.weekday()
            monday = today - timedelta(days=weekday)
            sunday = monday + timedelta(days=6)
            start_date = monday.isoformat()
            end_date = sunday.isoformat()
        return {
            "mode": "week",
            "status": status,
            "startDate": start_date,
            "endDate": end_date,
        }

    # Month mode (default)
    month = str(task_args.get("month") or "").strip()
    if month:
        if not MONTH_PATTERN.fullmatch(month):
            raise ValueError("month must be in YYYY-MM format")
    else:
        month = today.strftime("%Y-%m")

    year_num, month_num = (int(p) for p in month.split("-"))
    last_day = calendar.monthrange(year_num, month_num)[1]
    start_date = f"{month}-01"
    end_date = f"{month}-{last_day:02d}"

    return {
        "mode": "month",
        "status": status,
        "month": month,
        "startDate": start_date,
        "endDate": end_date,
    }


async def fetch_timesheet_reports_api(
    client: Any,
    url: str,
    headers: dict[str, str],
    params: dict[str, Any],
) -> list[dict[str, Any]]:
    payload = await fetch_json(client, url, params=params, headers=headers)
    data = payload.get("data") if isinstance(payload, dict) else None
    if isinstance(data, list):
        return [normalize_response_keys(item) for item in data]
    return []


async def fetch_timesheet_summary_api(
    client: Any,
    url: str,
    headers: dict[str, str],
    params: dict[str, Any],
) -> dict[str, Any]:
    payload = await fetch_json(client, url, params=params, headers=headers)
    data = payload.get("data") if isinstance(payload, dict) else payload
    if isinstance(data, dict):
        return normalize_response_keys(data)
    return {}
