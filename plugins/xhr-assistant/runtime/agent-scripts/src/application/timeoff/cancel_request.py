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
    raw_ids = task_args.get("request_ids") or task_args.get("requestIDs") or task_args.get("request_id") or task_args.get("id")
    request_ids = []
    if isinstance(raw_ids, list):
        for item in raw_ids:
            if isinstance(item, str):
                request_ids.extend([x.strip() for x in item.split(",") if x.strip()])
            elif item:
                request_ids.append(str(item).strip())
    elif isinstance(raw_ids, str) and raw_ids.strip():
        request_ids = [x.strip() for x in raw_ids.split(",") if x.strip()]

    if not request_ids:
        return error_result("request_ids_required",)

    endpoint_template = f"{api_base_url}/v1/to/time-off-requests/{{request_id}}/cancel"

    results = []
    async with http_client.session() as client:
        for request_id in request_ids:
            if not isinstance(request_id, str) or not request_id.strip():
                results.append({
                    "request_id": request_id,
                    "status_code": None,
                    "success": False,
                    "payload": {},
                    "error": {"message": "Invalid request ID"},
                })
                continue

            url = endpoint_template.format(request_id=request_id)
            try:
                status_code, payload = await request_json(client, "POST", url, headers=headers)
                success = 200 <= status_code < 300
                results.append({
                    "request_id": request_id,
                    "status_code": status_code,
                    "success": success,
                    "payload": payload,
                    "error": None if success else format_error(payload),
                })
            except Exception as exc:
                results.append({
                    "request_id": request_id,
                    "status_code": None,
                    "success": False,
                    "payload": {},
                    "error": format_error(exc=exc),
                })

    formatted = []
    success_count = 0
    for result in results:
        payload = result.get("payload")
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

        if result.get("success"):
            success_count += 1
        else:
            status_value = status_value or "FAILED"

        formatted.append({
            "request_id": result.get("request_id"),
            "time_off_type": time_off_name,
            "start_date": start_date,
            "end_date": end_date,
            "status": status_value,
            "status_code": result.get("status_code"),
            "error": result.get("error"),
        })

    requested = len(request_ids)
    failed_count = requested - success_count
    if requested == 0:
        overall_status = 400
    elif failed_count == 0:
        overall_status = 200
    elif success_count == 0:
        overall_status = results[0].get("status_code") or 500
    else:
        overall_status = 207

    if overall_status < 200 or overall_status >= 300:
        first_error = next((item.get("error") for item in formatted if item.get("error")), None)
        return error_result(str(first_error or f"Cancellation failed: {overall_status}"),)

    return ok_result({
        "data": formatted,
        "nextAction": "review_cancellation_status",
        "meta": {
            "requested": requested,
            "succeeded": success_count,
            "failed": failed_count,
        },
        "query": {"request_ids": request_ids},
    })
