from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_text
from src.shared.result import ok_result, error_result


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    request_id = clean_text(
        task_args.get("timesheetRequestId")
        or task_args.get("timesheet_request_id")
        or task_args.get("requestId")
        or task_args.get("id")
    )

    if not request_id:
        return error_result("timesheet_request_id_required",)

    endpoint = f"{api_base_url}/v1/atd/timesheets/{request_id}/approve"

    async with http_client.session() as client:
        try:
            response = await client.patch(endpoint, headers=headers)
            status_code = response.status_code
            try:
                payload = response.json()
            except Exception:
                payload = {}
        except Exception as exc:
            return error_result(str(exc),)

    data = payload.get("data") if isinstance(payload, dict) else None
    success = 200 <= status_code < 300

    if not success:
        return error_result(f"Timesheet approval failed: {status_code} {str(payload)}",)

    return ok_result({
        "data": data,
        "nextAction": "review_approval_status",
        "meta": {"timesheetRequestId": request_id},
        "query": {"timesheetRequestId": request_id},
    })
