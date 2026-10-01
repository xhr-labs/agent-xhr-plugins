from datetime import datetime, timezone
from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_int, clean_text
from src.shared.result import ok_result, error_result
from src.shared.http import format_error, request_json


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    year = clean_int(task_args.get("year"))
    if not year:
        year = datetime.now(timezone.utc).year

    start_date = clean_text(task_args.get("start_date") or task_args.get("startDate")) or f"{year}-01-01T00:00:00Z"
    end_date = clean_text(task_args.get("end_date") or task_args.get("endDate")) or f"{year}-12-31T23:59:59Z"

    endpoint = f"{api_base_url}/v1/to/holidays"
    query_params = {
        "startDate": start_date,
        "endDate": end_date,
    }

    async with http_client.session() as client:
        try:
            status_code, payload = await request_json(client, "GET", endpoint, params=query_params, headers=headers)
        except Exception as exc:
            return error_result(str(format_error(exc=exc)))

    if status_code >= 400:
        return error_result(str(format_error(payload)))

    holidays = payload.get("data") if isinstance(payload, dict) else payload
    if not isinstance(holidays, list):
        holidays = []

    formatted_holidays = []
    for h in holidays:
        if not isinstance(h, dict):
            continue
        formatted_holidays.append({
            "id": h.get("id"),
            "name": h.get("name"),
            "date": h.get("date"),
            "duration": h.get("duration"),
            "is_half_day": h.get("is_half_day", False),
            "description": h.get("description"),
        })

    return ok_result({
        "year": year,
        "holidays_count": len(formatted_holidays),
        "holidays": formatted_holidays,
        "query": query_params,
    })
