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
    reason = clean_text(task_args.get("reason"))

    if not request_id:
        return error_result("timesheet_request_id_required",)

    endpoint = f"{api_base_url}/v1/atd/timesheets/{request_id}/reject"
    payload = {"reason": reason}

    async with http_client.session() as client:
        try:
            response = await client.patch(endpoint, json=payload, headers=headers)
            status_code = response.status_code
            try:
                response_payload = response.json()
            except Exception:
                response_payload = {}
        except Exception as exc:
            return error_result(str(exc),)

    data = response_payload.get("data") if isinstance(response_payload, dict) else None
    success = 200 <= status_code < 300

    if not success:
        return error_result(f"Timesheet rejection failed: {status_code} {str(response_payload)}",)

    return ok_result({
        "data": data,
        "nextAction": "review_rejection_status",
        "meta": {"timesheetRequestId": request_id},
        "query": {"timesheetRequestId": request_id},
    })
