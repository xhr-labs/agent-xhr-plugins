from src.application.employee_requests.common import (
    call_json,
    has_version,
    require_uuid,
    success,
    value,
    version_error,
    write_headers,
)
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text
from src.shared.result import error_result


async def run(task_args, context: RequestContext, http_client):
    args = task_args if isinstance(task_args, dict) else {}
    request_id, failure = require_uuid(
        value(args, "request_id", "requestId", "id"), "request_id",
        lookup_hint="`list_my_requests` (match `request_number`, use field `id`)",
    )
    if failure:
        return failure
    body = clean_text(value(args, "body", "message"))
    if not body:
        return error_result("body_required: pass --body \"<message text>\"")
    if not has_version(args):
        return version_error("add_request_message")
    message = {"body": body}
    client_message_id = clean_text(value(args, "client_message_id", "clientMessageId"))
    if client_message_id:
        message["client_message_id"] = client_message_id
    payload, failure = await call_json(
        http_client, "POST", f"{context.api_base_url}/v1/erequest/requests/{request_id}/messages",
        headers=write_headers(context, args), body=message,
    )
    if failure:
        return failure
    return success(payload, request_id=request_id)
