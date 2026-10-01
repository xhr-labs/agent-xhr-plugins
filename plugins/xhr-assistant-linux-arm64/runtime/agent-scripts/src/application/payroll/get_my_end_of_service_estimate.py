from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any
from urllib.parse import quote
from zoneinfo import ZoneInfo

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.core.models.types import Header
from src.shared.http import format_error, request_json
from src.shared.normalize import clean_text
from src.shared.result import error_result, ok_result


def _user_today(context: RequestContext) -> date:
    """Today in the requester's timezone (``x-timezone`` header), UTC when absent or invalid."""
    timezone_name = clean_text(context.request_headers.get("x-timezone"))
    try:
        zone = ZoneInfo(timezone_name) if timezone_name else timezone.utc
    except Exception:
        zone = timezone.utc
    return datetime.now(zone).date()


def _end_of_current_month(context: RequestContext) -> str:
    today = _user_today(context)
    next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
    return (next_month - timedelta(days=1)).isoformat()


def _event_date(value: Any, context: RequestContext) -> str | None:
    text = clean_text(value)
    if not text:
        return _end_of_current_month(context)
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError:
        return None


def _string_list(value: Any) -> list[str]:
    """Flatten backend issue/assumption entries to user-facing text.

    The estimate API returns ``issues`` as objects (``code``, ``path``, ``severity``,
    ``message``); only the human-readable message may reach the agent.
    """
    if not isinstance(value, list):
        return []
    items: list[str] = []
    for item in value:
        if isinstance(item, dict):
            text = clean_text(item.get("message")) or clean_text(item.get("code"))
        else:
            text = clean_text(str(item))
        if text:
            items.append(text)
    return items


async def run(task_args, context: RequestContext, http_client: HttpClient):
    task_args = task_args if isinstance(task_args, dict) else {}
    employee_id = clean_text(context.request_headers.get(Header.X_EMPLOYEE_ID))
    if not employee_id:
        return error_result("missing_employee_id")

    target_employee_id = clean_text(task_args.get("employee_id")) or employee_id
    if target_employee_id != employee_id:
        groups = context.request_headers.get("xhr-employee-group")
        if groups is None:
            groups = context.request_headers.get("xhr-groups")
        if isinstance(groups, str):
            groups = groups.split(",")
        authorized = isinstance(groups, (list, tuple, set)) and any(
            isinstance(group, str) and group.strip().upper() in {"ADMIN", "HR_MANAGER"}
            for group in groups
        )
        if not authorized:
            return error_result("Only Admin or HR Manager users can estimate another employee's end-of-service benefit.")

    event_date = _event_date(task_args.get("event_date"), context)
    if event_date is None:
        return error_result("invalid_event_date: expected YYYY-MM-DD")

    endpoint = f"{context.api_base_url}/v1/ps/employees/{quote(target_employee_id, safe='')}/end-of-service/estimate"
    async with http_client.session() as client:
        try:
            status_code, payload = await request_json(
                client,
                "GET",
                endpoint,
                params={"event_date": event_date},
                headers=context.headers,
            )
        except Exception as exc:
            return error_result(str(format_error(exc=exc)))

    if status_code >= 400:
        return error_result(str(format_error(payload)))

    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, dict):
        return error_result("unexpected_end_of_service_estimate_response")

    return ok_result(
        {
            "event_date": data.get("event_date") or event_date,
            "event_type": data.get("event_type"),
            "termination_reason": data.get("termination_reason"),
            "status": data.get("status"),
            "status_reason": clean_text(data.get("status_reason")),
            "payable_amount": data.get("payable_amount"),
            "payable_currency": data.get("payable_currency"),
            "review_required": bool(data.get("review_required")),
            "review_note": clean_text(data.get("review_note")),
            "issues": _string_list(data.get("issues")),
            "assumptions": _string_list(data.get("assumptions")),
        }
    )
