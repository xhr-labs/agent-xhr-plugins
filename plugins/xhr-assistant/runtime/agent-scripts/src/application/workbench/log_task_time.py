from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text, is_uuid
from src.shared.result import error_result, ok_result


DATE_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")
DURATION_TOKEN_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)\s*([wdhm])$", re.IGNORECASE)


def parse_duration_to_minutes(duration_str: str | int | float | None) -> int | None:
    if duration_str is None:
        return None
    if isinstance(duration_str, (int, float)):
        return int(duration_str)

    cleaned = str(duration_str).strip().lower()
    if not cleaned:
        return None

    if cleaned.isdigit():
        return int(cleaned)

    tokens = cleaned.split()
    total_minutes = 0.0

    for token in tokens:
        match = DURATION_TOKEN_PATTERN.match(token)
        if not match:
            return None
        value, unit = match.groups()
        num = float(value)
        unit = unit.lower()
        if unit == "w":
            total_minutes += num * 5 * 8 * 60  # 1 week = 5 days = 40 hours
        elif unit == "d":
            total_minutes += num * 8 * 60      # 1 day = 8 hours
        elif unit == "h":
            total_minutes += num * 60
        elif unit == "m":
            total_minutes += num

    return int(round(total_minutes))


def _normalize_args(task_args: dict[str, Any]) -> dict[str, Any]:
    task_args = task_args if isinstance(task_args, dict) else {}
    return {
        "task_id": clean_text(task_args.get("task_id") or task_args.get("taskId")),
        "duration": task_args.get("duration") or task_args.get("duration_minutes") or task_args.get("durationMinutes") or task_args.get("time"),
        "work_date": clean_text(task_args.get("work_date") or task_args.get("workDate") or task_args.get("date")),
        "notes": clean_text(task_args.get("notes") or task_args.get("note") or task_args.get("description")),
    }


async def run(task_args: Any, context: RequestContext, http_client: HttpClient) -> dict[str, Any]:
    api_base_url = context.api_base_url
    headers = context.headers

    args = _normalize_args(task_args)
    task_id = args["task_id"]
    duration_raw = args["duration"]
    work_date = args["work_date"]
    notes = args["notes"]

    if not task_id:
        return error_result("task_id is required")
    if not is_uuid(task_id):
        return error_result("task_id must be a valid UUID")

    duration_minutes = parse_duration_to_minutes(duration_raw)
    if duration_minutes is None or duration_minutes <= 0:
        return error_result("duration must be a valid positive duration (e.g., '2h 30m', '120m', '1d', '4h')")

    if not work_date:
        work_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    elif not DATE_PATTERN.fullmatch(work_date):
        return error_result("work_date must be in YYYY-MM-DD format")

    url = f"{api_base_url}/v1/pm/tasks/{task_id}/timesheet-work-items"
    payload = {
        "items": [
            {
                "workDate": work_date,
                "work_date": work_date,
                "durationMinutes": duration_minutes,
                "duration_minutes": duration_minutes,
                **({"notes": notes} if notes else {}),
            }
        ]
    }

    async with http_client.session() as client:
        response = await client.post(url, json=payload, headers=headers)

    try:
        body = response.json()
    except Exception:
        body = {"message": response.text}

    if response.status_code >= 300:
        return error_result(f"Failed to log task time: {response.status_code} {str(body)}")

    hours = duration_minutes // 60
    mins = duration_minutes % 60
    duration_display = f"{hours}h {mins:02d}m" if hours > 0 and mins > 0 else f"{hours}h" if hours > 0 else f"{mins}m"

    return ok_result({
        "task_id": task_id,
        "work_date": work_date,
        "duration_minutes": duration_minutes,
        "duration_formatted": duration_display,
        "notes": notes,
        "action": "time_logged",
        "data": body.get("items") if isinstance(body, dict) and "items" in body else body,
    })
