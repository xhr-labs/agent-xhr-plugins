from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.result import ok_result, error_result

from src.shared.http import format_error, request_json


def _normalize_date(value):
    if isinstance(value, str):
        if "T" in value:
            return value.split("T", 1)[0]
        return value
    return None


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    request_id = task_args.get("request_id") or task_args.get("requestId") or task_args.get("id")
    if not isinstance(request_id, str) or not request_id.strip():
        return error_result("request_id_required",)

    endpoint = f"{api_base_url}/v1/to/time-off-requests/{request_id}/approve"

    async with http_client.session() as client:
        try:
            status_code, payload = await request_json(client, "POST", endpoint, headers=headers)
        except Exception as exc:
            return error_result(str(format_error(exc=exc)),)

    data = payload.get("data") if isinstance(payload, dict) else {}
    if not isinstance(data, dict):
        data = {}

    time_off_type = data.get("time_off_type") if isinstance(data, dict) else {}
    time_off_name = None
    if isinstance(time_off_type, dict):
        time_off_name = time_off_type.get("name")

    start_date = _normalize_date(data.get("start_date"))
    end_date = _normalize_date(data.get("end_date"))
    status_value = data.get("status")

    success = 200 <= status_code < 300
    if not success:
        status_value = status_value or "FAILED"

    formatted = {
        "request_id": request_id,
        "time_off_type": time_off_name,
        "start_date": start_date,
        "end_date": end_date,
        "status": status_value,
        "status_code": status_code,
        "error": None if success else format_error(payload),
    }

    if not success:
        return error_result(str(format_error(payload)),)

    return ok_result({
        "data": formatted,
        "nextAction": "review_approval_status",
        "meta": {"request_id": request_id},
        "query": {"request_id": request_id},
    })
