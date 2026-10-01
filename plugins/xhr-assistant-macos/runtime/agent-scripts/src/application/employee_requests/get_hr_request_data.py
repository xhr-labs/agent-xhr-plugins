from src.application.employee_requests.common import call_json, page_result, require_uuid, success, value
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text
from src.shared.result import error_result, ok_result


SUBRESOURCES = {
    "messages": "messages",
    "internal_notes": "internal-notes",
    "activities": "activities",
    "attachments": "attachments",
    "internal_attachments": "internal-attachments",
    "transfer_targets": "transfer-targets",
}


async def run(task_args, context: RequestContext, http_client):
    args = task_args if isinstance(task_args, dict) else {}
    action = clean_text(value(args, "action", "resource"))
    request_id = clean_text(value(args, "request_id", "requestId", "id"))
    if action not in {"view_counts", *SUBRESOURCES, "download_attachment", "download_internal_attachment"}:
        return error_result("unsupported_action: view_counts, messages, internal_notes, activities, attachments, internal_attachments, transfer_targets, download_attachment, or download_internal_attachment")
    if action != "view_counts":
        request_id, failure = require_uuid(request_id, "request_id", lookup_hint="`list_hr_requests --search <ER-number>` (field `id`)")
        if failure:
            return failure
    params = {"pageSize": max(1, min(int(value(args, "page_size", "pageSize") or 25), 100))}
    for key in ("cursor",):
        text = clean_text(value(args, key))
        if text:
            params[key] = text
    if action == "view_counts":
        path = "backoffice/requests/view-counts"
    elif action in SUBRESOURCES:
        path = f"backoffice/requests/{request_id}/{SUBRESOURCES[action]}"
    else:
        attachment_id = clean_text(value(args, "attachment_id", "attachmentId"))
        if not attachment_id:
            return error_result("attachment_id_required")
        folder = "internal-attachments" if action == "download_internal_attachment" else "attachments"
        path = f"backoffice/requests/{request_id}/{folder}/{attachment_id}/download"
        params = None
    payload, failure = await call_json(
        http_client, "GET", f"{context.api_base_url}/v1/erequest/{path}",
        headers=context.headers, params=params,
    )
    if failure:
        return failure
    if action in SUBRESOURCES or action == "view_counts":
        return ok_result(page_result(payload, "items") if action in SUBRESOURCES else {"data": payload.get("data") if isinstance(payload, dict) else None})
    return success(payload, action=action, request_id=request_id)
