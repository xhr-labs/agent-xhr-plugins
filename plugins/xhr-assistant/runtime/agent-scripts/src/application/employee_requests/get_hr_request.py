from src.application.employee_requests.common import call_json, require_uuid, success, value
from src.core.models.request_context import RequestContext


async def run(task_args, context: RequestContext, http_client):
    args = task_args if isinstance(task_args, dict) else {}
    request_id, failure = require_uuid(
        value(args, "request_id", "requestId", "id"), "request_id",
        lookup_hint="`list_hr_requests --search <ER-number>` (field `id`)",
    )
    if failure:
        return failure
    payload, failure = await call_json(
        http_client, "GET", f"{context.api_base_url}/v1/erequest/backoffice/requests/{request_id}",
        headers=context.headers,
    )
    if failure:
        return failure
    return success(payload, request_id=request_id)
