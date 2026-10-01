from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_text
from src.shared.result import ok_result, error_result
from src.shared.http import format_error, request_json


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    name = clean_text(task_args.get("name") or task_args.get("type_name"))
    if not name:
        return error_result("time_off_type_name_required")

    code = clean_text(task_args.get("code") or task_args.get("type_code"))
    color = clean_text(task_args.get("color")) or "#2563eb"
    is_paid = task_args.get("is_paid", True) if "is_paid" in task_args else task_args.get("isPaid", True)
    allocation_type = clean_text(task_args.get("allocation_type") or task_args.get("allocationType")) or "LIMITED"
    requires_attachment = task_args.get("requires_attachment", False) if "requires_attachment" in task_args else task_args.get("requiresAttachment", False)
    requires_reason = task_args.get("requires_reason", False) if "requires_reason" in task_args else task_args.get("requiresReason", False)

    category = "PAID" if bool(is_paid) else "UNPAID"
    body = {
        "name": name,
        "allocation_type": allocation_type.upper(),
        "category": category,
        "is_maternity_leave": False,
        "icon": "🌴",
    }
    if code:
        body["code"] = code
    if color:
        body["color"] = color

    endpoint = f"{api_base_url}/v1/to/time-off-types"

    async with http_client.session() as client:
        try:
            status_code, payload = await request_json(client, "POST", endpoint, json_data=body, headers=headers)
        except Exception as exc:
            return error_result(str(format_error(exc=exc)))

    if status_code >= 400:
        return error_result(str(format_error(payload)))

    data = payload.get("data") if isinstance(payload, dict) else payload
    return ok_result({
        "status": "CREATED",
        "time_off_type": data,
    })
