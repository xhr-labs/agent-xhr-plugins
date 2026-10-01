from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text, is_uuid
from src.shared.result import error_result, ok_result
from src.shared.workbench.task_format import format_task_detail


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    task_id = clean_text(task_args.get("task_id") or task_args.get("taskId") or task_args.get("id"))

    if not task_id:
        return error_result("task_id is required")
    if not is_uuid(task_id):
        return error_result(
            "task_id must be a valid UUID. Resolve it first with "
            "get_tasks --name \"<task title or keyword>\"."
        )

    url = f"{api_base_url}/v1/pm/tasks/{task_id}"
    async with http_client.session() as client:
        response = await client.get(url, headers=headers)

    try:
        payload = response.json()
    except Exception:
        payload = {}

    if response.status_code < 200 or response.status_code >= 300:
        return error_result(f"Task detail request failed: {response.status_code} {str(payload)}")

    task = payload.get("data") if isinstance(payload, dict) else None
    formatted = format_task_detail(task)
    if formatted is None:
        return error_result(f"Task {task_id} returned no data.")

    return ok_result({
        "task": formatted,
        "query": {"task_id": task_id, "endpoint": url},
    })
