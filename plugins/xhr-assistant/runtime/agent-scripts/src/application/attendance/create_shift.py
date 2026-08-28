import json

from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_int, clean_text, to_bool
from src.shared.result import ok_result, error_result


DAY_KEYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


def _hours(task_args, key, default):
    value = clean_int(
        task_args.get(f"target_{key}_hours")
        or task_args.get(f"target{key.title()}Hours")
        or task_args.get(f"{key}_hours")
    )
    if value is None:
        return default
    return value


def _minutes(task_args, key, default=0):
    value = clean_int(
        task_args.get(f"target_{key}_minutes")
        or task_args.get(f"target{key.title()}Minutes")
        or task_args.get(f"{key}_minutes")
    )
    if value is None:
        return default
    return value


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}

    name = clean_text(task_args.get("name") or task_args.get("shift_name") or task_args.get("shiftName"))
    description = clean_text(task_args.get("description")) or ""
    apply_public_holiday_target_hours = to_bool(
        task_args.get("apply_public_holiday_target_hours")
        or task_args.get("applyPublicHolidayTargetHours")
    )

    if not name:
        return error_result("shift_name_required")

    payload = {
        "name": name,
        "description": description,
        "apply_public_holiday_target_hours": apply_public_holiday_target_hours,
    }

    for day in DAY_KEYS:
        default_hours = 8 if day in {"monday", "tuesday", "wednesday", "thursday", "friday"} else 0
        hours = _hours(task_args, day, default_hours)
        minutes = _minutes(task_args, day, 0)

        if hours < 0 or hours > 24:
            return error_result(f"invalid_target_hours:{day}:{hours}")
        if minutes < 0 or minutes > 59:
            return error_result(f"invalid_target_minutes:{day}:{minutes}")

        payload[f"target_{day}_hours"] = hours
        payload[f"target_{day}_minutes"] = minutes

    endpoint = f"{api_base_url}/v1/atd/shifts"

    async with http_client.session() as client:
        try:
            response = await client.post(endpoint, json=payload, headers=headers)
            status_code = response.status_code
            try:
                response_payload = response.json()
            except Exception:
                response_payload = {}
        except Exception as exc:
            return error_result(str(exc))

    if status_code < 200 or status_code >= 300:
        return error_result(f"Create shift failed: {status_code} {json.dumps(response_payload, ensure_ascii=False)}")

    data = response_payload.get("data") if isinstance(response_payload, dict) else None

    return ok_result({
        "data": data,
        "payload": payload,
        "meta": {
            "name": name,
            "endpoint": endpoint,
        },
    })
