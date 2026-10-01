import json

from src.application.employee_requests.common import (
    call_json,
    has_version,
    require_body_keys,
    require_uuid,
    success,
    value,
    version_error,
    write_headers,
)
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text
from src.shared.result import error_result


ACTION_PATHS = {
    "add_public_message": ("POST", "messages"),
    "add_internal_note": ("POST", "internal-notes"),
    "assign": ("POST", "assignments"),
    "transfer": ("POST", "transfers"),
    "transition": ("POST", "transitions"),
    "change_priority": ("PATCH", "priority"),
    "override_due_date": ("PATCH", "due-date"),
    "initialize_public_attachment": ("POST", "public-attachment-intents"),
    "complete_public_attachment": ("POST", "public-attachment-intents/{intent_id}/completion"),
    "claim_public_attachment": ("POST", "attachments"),
    "initialize_internal_attachment": ("POST", "attachments/intents"),
    "complete_internal_attachment": ("POST", "attachments/intents/{intent_id}/completion"),
    "claim_internal_attachment": ("POST", "internal-attachments"),
}

# Backend payload contract per action (snake_case; mirrors employee-requests-app clients).
ACTION_BODY = {
    "add_public_message": (("body",), ("client_message_id",)),
    "add_internal_note": (("body",), ("client_note_id",)),
    "assign": (("assignee_id",), ("reason",)),
    "transfer": (("queue_id",), ("assignee_id", "reason")),
    "transition": (("transition_key",), ("reason", "resolution_code", "resolution_summary")),
    "change_priority": (("priority", "reason"), ()),
    "override_due_date": (("resolution_due_at", "reason"), ()),
    "initialize_public_attachment": (("display_name", "mime_type", "byte_size"), ()),
    "initialize_internal_attachment": (("display_name", "mime_type", "byte_size"), ("visibility",)),
    "claim_public_attachment": (("intent_id",), ()),
    "claim_internal_attachment": (("intent_id",), ()),
    "complete_public_attachment": ((), ()),
    "complete_internal_attachment": ((), ()),
}

PRIORITIES = ("LOW", "NORMAL", "HIGH", "URGENT")


def _body(args: dict, action: str):
    raw = value(args, "body", "payload", "body_json")
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return None
        if isinstance(parsed, dict):
            return parsed
        return None

    required, optional = ACTION_BODY.get(action, ((), ()))
    result = {}
    for source in (*required, *optional):
        camel = "".join([source.split("_")[0]] + [part.title() for part in source.split("_")[1:]])
        candidate = value(args, source, camel)
        if candidate is not None and (not isinstance(candidate, str) or clean_text(candidate) is not None):
            result[source] = candidate
    return result


async def run(task_args, context: RequestContext, http_client):
    args = task_args if isinstance(task_args, dict) else {}
    action = clean_text(value(args, "action", "operation"))
    if action not in ACTION_PATHS:
        return error_result(f"unsupported_action: {', '.join(sorted(ACTION_PATHS))}")
    request_id, failure = require_uuid(
        value(args, "request_id", "requestId", "id"), "request_id",
        lookup_hint="`list_hr_requests --search <ER-number>` (field `id`) or `get_hr_request`",
    )
    if failure:
        return failure
    method, path = ACTION_PATHS[action]
    intent_id = clean_text(value(args, "intent_id", "intentId"))
    if "{intent_id}" in path:
        intent_id, failure = require_uuid(intent_id, "intent_id", lookup_hint="the `id` returned by the initialize_* action")
        if failure:
            return failure
        path = path.replace("{intent_id}", intent_id)

    body = _body(args, action)
    if body is None:
        return error_result("body_json_invalid: --body-json must be a JSON object")
    required, optional = ACTION_BODY[action]
    if action in {"complete_public_attachment", "complete_internal_attachment"}:
        body = None
    else:
        failure = require_body_keys(body, action, required, optional)
        if failure:
            return failure
        if action == "change_priority" and str(body.get("priority")).upper() not in PRIORITIES:
            return error_result(f"priority_invalid: '{body.get('priority')}'. Allowed values: {', '.join(PRIORITIES)}.")
        if action == "change_priority":
            body["priority"] = str(body["priority"]).upper()
        if action == "initialize_internal_attachment":
            body.setdefault("visibility", "INTERNAL")

    # Every HR mutation is versioned by the backend (428 without If-Match, 400 when unquoted).
    if not has_version(args):
        return version_error(action)

    endpoint = f"{context.api_base_url}/v1/erequest/backoffice/requests/{request_id}/{path}"
    payload, failure = await call_json(
        http_client, method, endpoint, headers=write_headers(context, args), body=body,
    )
    if failure:
        return failure
    return success(payload, request_id=request_id, action=action)
