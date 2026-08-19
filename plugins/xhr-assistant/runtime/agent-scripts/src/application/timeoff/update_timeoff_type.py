from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_text
from src.shared.result import ok_result, error_result
from src.shared.http import format_error, request_json


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    type_id = clean_text(task_args.get("type_id") or task_args.get("typeId") or task_args.get("id"))
    if not type_id:
        return error_result("type_id_required")

    name = clean_text(task_args.get("name") or task_args.get("type_name"))
    color = clean_text(task_args.get("color"))
    is_paid = task_args.get("is_paid") if "is_paid" in task_args else task_args.get("isPaid")
    requires_attachment = task_args.get("requires_attachment") if "requires_attachment" in task_args else task_args.get("requiresAttachment")
    requires_reason = task_args.get("requires_reason") if "requires_reason" in task_args else task_args.get("requiresReason")

    body = {}
    if name:
        body["name"] = name
    if color:
        body["color"] = color
    if is_paid is not None:
        body["isPaid"] = bool(is_paid)
    if requires_attachment is not None:
        body["requiresAttachment"] = bool(requires_attachment)
    if requires_reason is not None:
        body["requiresReason"] = bool(requires_reason)

    endpoint = f"{api_base_url}/v1/to/time-off-types/{type_id}"

    async with http_client.session() as client:
        try:
            status_code, payload = await request_json(client, "PUT", endpoint, json_data=body, headers=headers)
        except Exception as exc:
            return error_result(str(format_error(exc=exc)))

    if status_code >= 400:
        return error_result(str(format_error(payload)))

    return ok_result({
        "status": "UPDATED",
        "type_id": type_id,
        "response": payload.get("data") if isinstance(payload, dict) else payload,
    })
