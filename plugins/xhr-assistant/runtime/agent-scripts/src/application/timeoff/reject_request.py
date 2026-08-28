from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_text
from src.shared.result import ok_result, error_result
from src.shared.http import format_error, request_json


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    request_id = clean_text(task_args.get("request_id") or task_args.get("requestId") or task_args.get("id"))
    if not request_id:
        return error_result("request_id_required")

    reject_reason = clean_text(task_args.get("reject_reason") or task_args.get("rejectReason") or task_args.get("reason") or task_args.get("note"))

    endpoint = f"{api_base_url}/v1/to/time-off-requests/{request_id}/reject"
    body = {"rejectReason": reject_reason} if reject_reason else {}

    async with http_client.session() as client:
        try:
            status_code, payload = await request_json(client, "POST", endpoint, json_data=body, headers=headers)
        except Exception as exc:
            return error_result(str(format_error(exc=exc)))

    if status_code >= 400:
        return error_result(str(format_error(payload)))

    data = payload.get("data") if isinstance(payload, dict) else {}
    return ok_result({
        "request_id": request_id,
        "status": "REJECTED",
        "reject_reason": reject_reason,
        "response": data,
    })
