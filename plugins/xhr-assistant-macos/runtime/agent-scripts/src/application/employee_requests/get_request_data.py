from src.application.employee_requests.common import call_json, page_result, require_uuid, success, value
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text
from src.shared.result import error_result, ok_result


RESOURCES = {"messages": "messages", "activities": "activities", "attachments": "attachments"}


async def run(task_args, context: RequestContext, http_client):
    args = task_args if isinstance(task_args, dict) else {}
    action = clean_text(value(args, "action", "resource"))
    request_id = clean_text(value(args, "request_id", "requestId", "id"))
    if action not in {*RESOURCES, "download_attachment"}:
        return error_result("unsupported_action: messages, activities, attachments, or download_attachment")
    request_id, failure = require_uuid(request_id, "request_id", lookup_hint="`list_my_requests` (match `request_number`, use field `id`)")
    if failure:
        return failure
    params = {"pageSize": max(1, min(int(value(args, "page_size", "pageSize") or 25), 100))}
    cursor = clean_text(value(args, "cursor"))
    if cursor:
        params["cursor"] = cursor
    if action in RESOURCES:
        path = f"requests/{request_id}/{RESOURCES[action]}"
    else:
        attachment_id = clean_text(value(args, "attachment_id", "attachmentId"))
        if not attachment_id:
            return error_result("attachment_id_required")
        path = f"requests/{request_id}/attachments/{attachment_id}/download"
        params = None
    payload, failure = await call_json(
        http_client, "GET", f"{context.api_base_url}/v1/erequest/{path}",
        headers=context.headers, params=params,
    )
    if failure:
        return failure
    if action in RESOURCES:
        return ok_result(page_result(payload, "items"))
    return success(payload, action=action, request_id=request_id)
