from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_text
from src.shared.result import ok_result, error_result


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    args = task_args if isinstance(task_args, dict) else {}
    project_id = clean_text(args.get("project_id") or args.get("projectId"))
    page_id = clean_text(args.get("page_id") or args.get("pageId"))

    if not project_id or not page_id:
        return error_result("project_id and page_id are required",)

    url = f"{api_base_url}/v1/pm/projects/{project_id}/wiki/pages/{page_id}"

    async with http_client.session() as client:
        response = await client.get(url, headers=headers)
        try:
            payload = response.json()
        except Exception:
            payload = {}

    data = None
    if isinstance(payload, dict):
        data = payload.get("data")

    if response.status_code < 200 or response.status_code >= 300:
        return error_result(f"Page content request failed: {response.status_code} {str(payload)}",)

    if not isinstance(data, dict):
        return ok_result({
            "data": None,
            "project_id": project_id,
            "page_id": page_id,
        })

    return ok_result({
        "data": {
            "page_id": data.get("id"),
            "title": data.get("title"),
            "content": data.get("content"),
        },
        "project_id": project_id,
        "page_id": page_id,
    })
