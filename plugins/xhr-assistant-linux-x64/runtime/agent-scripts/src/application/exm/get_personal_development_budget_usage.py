from __future__ import annotations

from datetime import date
from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.core.models.types import Header
from src.shared.http import format_error, request_json
from src.shared.normalize import clean_int, clean_text
from src.shared.result import error_result, ok_result


USAGE_PATH = "/v1/exm/agent/personal-development-budget/usage"
MIN_YEAR = 1900
MAX_YEAR = 9999


def _iso_date(value: Any, label: str) -> tuple[str | None, str | None]:
    """Return (iso_date, error). ``None, None`` when the argument is absent."""
    text = clean_text(value)
    if not text:
        return None, None
    try:
        return date.fromisoformat(text).isoformat(), None
    except ValueError:
        return None, f"invalid_{label}: expected YYYY-MM-DD"


def _build_request_body(task_args: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    """Normalize ``year`` / ``date_from`` / ``date_to`` into the backend request body.

    The backend treats every filter as optional and defaults to an all-time report,
    so an empty body is the normal case. ``year`` is a convenience that expands to a
    full calendar year and cannot be combined with an explicit range.
    """
    year = clean_int(task_args.get("year"))
    date_from, from_error = _iso_date(task_args.get("date_from") or task_args.get("dateFrom"), "date_from")
    date_to, to_error = _iso_date(task_args.get("date_to") or task_args.get("dateTo"), "date_to")

    if from_error:
        return None, from_error
    if to_error:
        return None, to_error

    if year is not None:
        if date_from or date_to:
            return None, "conflicting_period: pass either --year or --date-from/--date-to, not both"
        if year < MIN_YEAR or year > MAX_YEAR:
            return None, f"invalid_year: expected a calendar year between {MIN_YEAR} and {MAX_YEAR}"
        return {"date_from": f"{year}-01-01", "date_to": f"{year}-12-31"}, None

    if date_from and date_to and date_from > date_to:
        return None, "invalid_period: date_from must be on or before date_to"

    body: dict[str, Any] = {}
    if date_from:
        body["date_from"] = date_from
    if date_to:
        body["date_to"] = date_to
    return body, None


def _count(value: Any) -> int:
    number = clean_int(value)
    return number if number is not None and number >= 0 else 0


def _categories(value: Any) -> list[dict[str, Any]]:
    """Reduce category breakdown entries to user-facing fields.

    The backend (dev, 2026-09-09) returns objects such as ``{"category_id", "category_code",
    "category_name", "used_employee_count", "expense_count", "used_employee_ids"}``. Only the
    name and the two counts are kept: ids and the nested employee-id list must never reach
    the agent. Plain strings are accepted as a bare name for forward compatibility.
    """
    if not isinstance(value, list):
        return []
    categories: list[dict[str, Any]] = []
    for item in value:
        if isinstance(item, dict):
            name = (
                clean_text(item.get("category_name"))
                or clean_text(item.get("name"))
                or clean_text(item.get("category_code"))
                or clean_text(item.get("code"))
            )
            if not name:
                continue
            categories.append(
                {
                    "name": name,
                    "used_employee_count": _count(item.get("used_employee_count")),
                    "expense_count": _count(item.get("expense_count")),
                }
            )
        elif item is not None:
            name = clean_text(str(item))
            if name:
                categories.append({"name": name, "used_employee_count": None, "expense_count": None})
    return categories


def _usage_rate_percent(used: int, scoped: int | None) -> float | None:
    if scoped is None or scoped <= 0:
        return None
    return round(used * 100 / scoped, 1)


def _request_error(status_code: int, payload: Any) -> str:
    if status_code in (401, 403):
        return (
            "permission_denied: the signed-in user is not allowed to view the "
            "personal development budget usage report"
        )
    message = format_error(payload).get("message") or "Request failed"
    return f"personal_development_budget_usage_request_failed: {status_code} {message}"


async def run(task_args, context: RequestContext, http_client: HttpClient):
    task_args = task_args if isinstance(task_args, dict) else {}
    employee_id = clean_text(context.request_headers.get(Header.X_EMPLOYEE_ID))
    if not employee_id:
        return error_result("missing_employee_id")

    body, body_error = _build_request_body(task_args)
    if body_error:
        return error_result(body_error)

    endpoint = f"{context.api_base_url}{USAGE_PATH}"
    try:
        async with http_client.session() as client:
            status_code, payload = await request_json(
                client, "POST", endpoint, json=body, headers=context.headers
            )
    except Exception as exc:
        return error_result(str(format_error(exc=exc)))

    if status_code >= 400:
        return error_result(_request_error(status_code, payload))

    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, dict):
        return error_result("unexpected_personal_development_budget_usage_response")

    used_employee_count = _count(data.get("used_employee_count"))
    scoped_employee_count = clean_int(data.get("scoped_employee_count"))
    statuses = [text for text in (clean_text(item) for item in data.get("statuses") or []) if text]

    # ``used_employee_ids`` is deliberately dropped: the agent must never expose
    # internal employee identifiers, and the count already carries the answer.
    return ok_result(
        {
            "used_employee_count": used_employee_count,
            "scoped_employee_count": scoped_employee_count,
            "usage_rate_percent": _usage_rate_percent(used_employee_count, scoped_employee_count),
            "expense_count": _count(data.get("expense_count")),
            "categories": _categories(data.get("categories")),
            "statuses": statuses,
            "date_from": clean_text(data.get("date_from")) or body.get("date_from"),
            "date_to": clean_text(data.get("date_to")) or body.get("date_to"),
        }
    )
