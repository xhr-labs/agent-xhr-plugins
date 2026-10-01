from src.application.employee_requests.common import call_json, require_uuid, success, value
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text


async def run(task_args, context: RequestContext, http_client):
    """Employee-scoped request type detail: form_schema, instructions and attachment_policy.

    This is the only employee-visible source of the form field keys required by submit_request.
    """
    args = task_args if isinstance(task_args, dict) else {}
    request_type_id, failure = require_uuid(
        value(args, "request_type_id", "requestTypeId", "id"), "request_type_id",
        lookup_hint="`get_request_types` (match `name`, use field `id`)",
    )
    if failure:
        return failure
    headers = dict(context.headers)
    locale = clean_text(value(args, "locale"))
    if locale:
        headers["X-Locale"] = locale
    payload, failure = await call_json(
        http_client, "GET", f"{context.api_base_url}/v1/erequest/request-types/{request_type_id}",
        headers=headers,
    )
    if failure:
        return failure
    data = payload.get("data") if isinstance(payload, dict) else None
    fields = []
    if isinstance(data, dict):
        schema = data.get("form_schema") or {}
        for field in (schema.get("fields") or []) if isinstance(schema, dict) else []:
            if not isinstance(field, dict):
                continue
            entry = {
                "key": field.get("key"),
                "type": field.get("type"),
                "label": field.get("label"),
                "required": bool(field.get("required")),
            }
            if field.get("options"):
                entry["allowed_values"] = [option.get("value") for option in field["options"] if isinstance(option, dict)]
            fields.append(entry)
    return success(
        payload,
        request_type_id=request_type_id,
        answer_contract={
            "fields": fields,
            "answers_format": {
                "SHORT_TEXT": "string (<=255)", "LONG_TEXT": "string (<=8000)", "DATE": "YYYY-MM-DD string",
                "SELECT": "one of allowed_values (the value, not the label)", "BOOLEAN": "true/false JSON boolean",
                "EMPLOYEE_REFERENCE": "employee UUID", "DOCUMENT_UPLOAD": "array of completed attachment intent UUIDs (upload happens in the app, not in chat)",
            },
            "note": "answers keys must be exactly the field keys above; omit optional fields left blank.",
        },
    )
