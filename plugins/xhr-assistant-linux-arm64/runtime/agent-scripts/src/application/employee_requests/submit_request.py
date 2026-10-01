import json

from src.application.employee_requests.common import call_json, success, value, write_headers
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text, normalize_list
from src.shared.result import error_result


def _json_object(raw):
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, dict) else None
    return None


async def run(task_args, context: RequestContext, http_client):
    args = task_args if isinstance(task_args, dict) else {}
    request_type_id = clean_text(value(args, "request_type_id", "requestTypeId"))
    answers = _json_object(value(args, "answers", "answers_json"))
    version = value(args, "request_type_version", "requestTypeVersion", "version")
    try:
        version = int(version)
    except (TypeError, ValueError):
        version = None
    if not request_type_id or version is None or version <= 0 or answers is None:
        return error_result("request_type_id, positive request_type_version, and answers object are required")

    payload = {
        "request_type_id": request_type_id,
        "request_type_version": version,
        "answers": answers,
        "completed_attachment_intent_ids": normalize_list(
            value(args, "completed_attachment_intent_ids", "completedAttachmentIntentIds")
        ),
    }
    response, failure = await call_json(
        http_client,
        "POST",
        f"{context.api_base_url}/v1/erequest/requests",
        headers=write_headers(context, args),
        body=payload,
    )
    if failure:
        return failure
    data = response.get("data") if isinstance(response, dict) else None
    return success(response, request_id=(data or {}).get("id") if isinstance(data, dict) else None)
