from datetime import UTC, datetime

from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.core.models.types import Header
from src.shared.normalize import clean_int, clean_text
from src.shared.result import ok_result, error_result

from src.shared.http import format_error, request_json


def _clean_number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0


def _first_field(entry, *keys):
    for key in keys:
        if key in entry:
            return entry.get(key)
    return None


def _is_true(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on", "enabled"}
    return False


def _requestable_balance(entry):
    available_balance = _clean_number(_first_field(entry, "available_balance", "availableBalance"))
    advance_leave_limit = (
        _clean_number(_first_field(entry, "advance_leave_limit_days", "advanceLeaveLimitDays"))
        if _is_true(_first_field(entry, "advance_leave_enabled", "advanceLeaveEnabled"))
        else 0
    )
    return available_balance + advance_leave_limit


def _format_balance(entry):
    if not isinstance(entry, dict):
        return None
    return {
        "time_off_type_id": _first_field(entry, "time_off_type_id", "timeOffTypeId"),
        "time_off_type_name": _first_field(entry, "time_off_type_name", "timeOffTypeName"),
        "current_balance": _first_field(entry, "current_balance", "currentBalance"),
        "pending_balance": _first_field(entry, "pending_balance", "pendingBalance"),
        "available_balance": _first_field(entry, "available_balance", "availableBalance"),
        "advance_leave_enabled": _first_field(entry, "advance_leave_enabled", "advanceLeaveEnabled"),
        "advance_leave_limit_days": _first_field(entry, "advance_leave_limit_days", "advanceLeaveLimitDays"),
        "requestable_balance": _requestable_balance(entry),
        "year": entry.get("year"),
    }


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    year = clean_int(task_args.get("year"))
    if year is None:
        year = datetime.now(UTC).year
    employee_id = clean_text(task_args.get("employee_id") or task_args.get("employeeId") or context.request_headers.get(Header.X_EMPLOYEE_ID))

    if not employee_id:
        return error_result("missing_required_fields",)

    url = f"{api_base_url}/v1/to/time-off-balances/search"
    params = {
        "year": year,
        "employeeId": employee_id,
    }

    async with http_client.session() as client:
        try:
            status_code, response_payload = await request_json(client, "GET", url, params=params, headers=headers)
        except Exception as exc:
            return error_result(str(format_error(exc=exc)),)

    if isinstance(response_payload, dict):
        data = response_payload.get("data", []) or []
    else:
        data = []

    formatted = []
    for entry in data:
        item = _format_balance(entry)
        if item:
            formatted.append(item)

    if status_code >= 400:
        return error_result(str(format_error(response_payload)),)

    return ok_result({
        "items_count": len(formatted),
        "items": formatted,
        "query": params,
    })
