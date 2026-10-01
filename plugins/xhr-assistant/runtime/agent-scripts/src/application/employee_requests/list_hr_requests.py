from src.application.employee_requests.common import call_json, page_result, require_enum, require_uuid, value
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text
from src.shared.result import ok_result


ALIASES = {
    "page_size": "pageSize", "request_type_id": "requestTypeId", "status_key": "statusKey", "assignee_id": "assigneeId",
    "queue_id": "queueId", "sla_risk": "slaRisk", "created_from": "createdFrom", "created_to": "createdTo",
}
TEXT_KEYS = ("status_key", "search", "created_from", "created_to", "cursor")
UUID_KEYS = ("queue_id", "request_type_id", "assignee_id")
ENUMS = {
    "assignment": ("any", "mine", "unassigned"),
    "sla_risk": ("normal", "warning", "breached"),
    "view": ("inbox", "mine", "unassigned", "overdue", "completed"),
    "priority": ("LOW", "NORMAL", "HIGH", "URGENT"),
    "sort": ("createdAt", "updatedAt", "resolutionDueAt", "priority"),
    "order": ("asc", "desc"),
}


async def run(task_args, context: RequestContext, http_client):
    args = task_args if isinstance(task_args, dict) else {}
    params = {}
    for key in TEXT_KEYS:
        text = clean_text(value(args, key, ALIASES.get(key, key)))
        if text:
            params[ALIASES.get(key, key)] = text
    for key in UUID_KEYS:
        raw = value(args, key, ALIASES.get(key, key))
        if raw is None or clean_text(raw) is None:
            continue
        uuid_value, failure = require_uuid(raw, key, lookup_hint="the corresponding list tool (list_queues, list_request_types, list_eligible_assignees)")
        if failure:
            return failure
        params[ALIASES.get(key, key)] = uuid_value
    for key, allowed in ENUMS.items():
        normalized, failure = require_enum(value(args, key, ALIASES.get(key, key)), key, allowed)
        if failure:
            return failure
        if normalized and not (key == "assignment" and normalized == "any"):
            params[ALIASES.get(key, key)] = normalized
    raw_size = value(args, "page_size", "pageSize")
    try:
        page_size = int(raw_size) if raw_size is not None else 25
    except (TypeError, ValueError):
        page_size = 25
    params["pageSize"] = max(1, min(page_size, 100))
    payload, failure = await call_json(
        http_client, "GET", f"{context.api_base_url}/v1/erequest/backoffice/requests",
        headers=context.headers, params=params,
    )
    if failure:
        return failure
    return ok_result(page_result(payload, "requests"))
