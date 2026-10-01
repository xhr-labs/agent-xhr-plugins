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

    endpoint = f"{api_base_url}/v1/to/time-off-types/{type_id}"

    async with http_client.session() as client:
        try:
            status_code, payload = await request_json(client, "DELETE", endpoint, headers=headers)
        except Exception as exc:
            return error_result(str(format_error(exc=exc)))

    if status_code >= 400:
        return error_result(str(format_error(payload)))

    return ok_result({
        "status": "DELETED",
        "type_id": type_id,
        "message": f"Time off type {type_id} has been deleted successfully.",
    })
