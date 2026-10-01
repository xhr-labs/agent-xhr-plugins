import json

from src.application.employee_requests.common import call_json, require_uuid, success, value, write_headers
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text
from src.shared.result import error_result


async def run(task_args, context: RequestContext, http_client):
    args = task_args if isinstance(task_args, dict) else {}
    action = clean_text(value(args, "action", "operation"))
    queue_id = clean_text(value(args, "queue_id", "queueId", "id"))
    allowed = {"create", "update", "retire"}
    if action not in allowed:
        return error_result("action_required: create, update, or retire")
    if action != "create":
        queue_id, failure = require_uuid(queue_id, "queue_id", lookup_hint="`list_queues` (field `id`)")
        if failure:
            return failure
    body = value(args, "body", "payload", "body_json")
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            return error_result("body_json_invalid")
    if not isinstance(body, dict):
        body = {}
    if action in {"create", "update"} and not body:
        for key in ("queue_key", "name", "description"):
            candidate = value(args, key, "".join([key.split("_")[0]] + [part.title() for part in key.split("_")[1:]]))
            if candidate is not None:
                body[key] = candidate
    paths = {
        "create": ("POST", "queues"),
        "update": ("PATCH", f"queues/{queue_id}"),
        "retire": ("POST", f"queues/{queue_id}/retirement"),
    }
    method, path = paths[action]
    payload, failure = await call_json(
        http_client, method, f"{context.api_base_url}/v1/erequest/backoffice/{path}",
        headers=write_headers(context, args), body=body if action != "retire" else None,
    )
    if failure:
        return failure
    return success(payload, action=action, queue_id=queue_id)
