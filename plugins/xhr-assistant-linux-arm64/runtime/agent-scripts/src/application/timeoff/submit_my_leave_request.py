from datetime import date, timedelta

from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_text
from src.shared.result import ok_result, error_result

from src.shared.http import format_error, request_json


VALID_DAY_TYPES = {"FULL_DAY", "MORNING", "AFTERNOON"}


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    start_date = clean_text(task_args.get("start_date") or task_args.get("startDate"))
    end_date = clean_text(task_args.get("end_date") or task_args.get("endDate"))
    time_off_type_id = clean_text(task_args.get("time_off_type_id") or task_args.get("timeOffTypeId"))
    day_type = (
        clean_text(task_args.get("day_type") or task_args.get("dayType")) or "FULL_DAY"
    ).upper()
    notes = clean_text(task_args.get("notes"))

    missing_fields = []
    if not start_date:
        missing_fields.append("start_date")
    if not end_date:
        missing_fields.append("end_date")
    if not time_off_type_id:
        missing_fields.append("time_off_type_id")

    if missing_fields:
        return error_result(f"missing_required_fields: {', '.join(missing_fields)}",)
    if day_type not in VALID_DAY_TYPES:
        return error_result(
            "invalid_day_type: expected FULL_DAY, MORNING, or AFTERNOON",
        )

    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError:
        return error_result("invalid_date_format: expected YYYY-MM-DD",)
    if end < start:
        return error_result("invalid_date_range: end_date must be on or after start_date",)

    request_days = []
    request_date = start
    while request_date <= end:
        request_days.append({
            "request_date": f"{request_date.isoformat()}T00:00:00+00:00",
            "day_type": day_type,
        })
        request_date += timedelta(days=1)

    payload = {
        "start_date": start_date,
        "end_date": end_date,
        "time_off_type_id": time_off_type_id,
        "request_days": request_days,
    }
    if notes:
        payload["notes"] = notes

    url = f"{api_base_url}/v1/to/time-off-requests"

    async with http_client.session() as client:
        try:
            status_code, response_payload = await request_json(client, "POST", url, json=payload, headers=headers)
        except Exception as exc:
            return error_result(str(format_error(exc=exc)),)

    if status_code >= 400:
        return error_result(str(format_error(response_payload)),)

    return ok_result({
        "data": response_payload.get("data") if isinstance(response_payload, dict) else None,
    })
