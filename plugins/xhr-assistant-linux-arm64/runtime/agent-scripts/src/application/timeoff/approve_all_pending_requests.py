from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.result import ok_result, error_result
from src.shared.http import format_error, request_json


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    endpoint = f"{api_base_url}/v1/to/time-off-requests/approve-pending"

    async with http_client.session() as client:
        try:
            status_code, payload = await request_json(client, "POST", endpoint, headers=headers)
        except Exception as exc:
            return error_result(str(format_error(exc=exc)))

    if status_code >= 400:
        return error_result(str(format_error(payload)))

    return ok_result({
        "status": "SUCCESS",
        "message": "All pending time-off requests have been approved successfully.",
        "response": payload.get("data") if isinstance(payload, dict) else payload,
    })
