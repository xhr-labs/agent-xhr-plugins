import json

from src.application.employee_requests.common import call_json, require_uuid, success, value, write_headers
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text
from src.shared.result import error_result


async def run(task_args, context: RequestContext, http_client):
    args = task_args if isinstance(task_args, dict) else {}
    action = clean_text(value(args, "action", "operation"))
    request_id, failure = require_uuid(
        value(args, "request_id", "requestId", "id"), "request_id",
        lookup_hint="`list_hr_requests --search <ER-number>` (field `id`)",
    )
    if failure:
        return failure
    if action not in {"execute_operation", "get_operation", "place_hold", "release_hold"}:
        return error_result("unsupported_action: execute_operation, get_operation, place_hold, or release_hold")
    operation_id = clean_text(value(args, "operation_id", "operationId"))
    hold_id = clean_text(value(args, "hold_id", "holdId"))
    if action == "get_operation" and not operation_id:
        return error_result("operation_id_required")
    if action == "release_hold" and not hold_id:
        return error_result("hold_id_required")
    body = value(args, "body", "payload", "body_json")
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            return error_result("body_json_invalid")
    if action == "execute_operation":
        path, method = "operations", "POST"
    elif action == "get_operation":
        path, method, body = f"operations/{operation_id}", "GET", None
    elif action == "place_hold":
        path, method = "legal-holds", "POST"
    else:
        path, method = f"legal-holds/{hold_id}/release", "POST"
    payload, failure = await call_json(
        http_client, method,
        f"{context.api_base_url}/v1/erequest/backoffice/privacy/requests/{request_id}/{path}",
        headers=context.headers if method == "GET" else write_headers(context, args),
        body=body,
    )
    if failure:
        return failure
    return success(payload, action=action, request_id=request_id)
