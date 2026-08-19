from __future__ import annotations

from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text, is_uuid
from src.shared.result import error_result, ok_result


def _normalize_args(task_args: dict[str, Any]) -> dict[str, Any]:
    task_args = task_args if isinstance(task_args, dict) else {}
    try:
        page = int(task_args.get("page") or task_args.get("page_number") or 0)
    except (ValueError, TypeError):
        page = 0
    try:
        size = int(task_args.get("size") or task_args.get("page_size") or 20)
    except (ValueError, TypeError):
        size = 20

    return {
        "task_id": clean_text(task_args.get("task_id") or task_args.get("taskId")),
        "page": page,
        "size": size,
    }


async def run(task_args: Any, context: RequestContext, http_client: HttpClient) -> dict[str, Any]:
    api_base_url = context.api_base_url
    headers = context.headers

    args = _normalize_args(task_args)
    task_id = args["task_id"]
    page = args["page"]
    size = args["size"]

    if not task_id:
        return error_result("task_id is required")
    if not is_uuid(task_id):
        return error_result("task_id must be a valid UUID")

    url = f"{api_base_url}/v1/pm/task-comments/list"
    params = {
        "taskId": task_id,
        "page": page,
        "size": size,
    }

    async with http_client.session() as client:
        response = await client.get(url, params=params, headers=headers)

    try:
        body = response.json()
    except Exception:
        body = {}

    if response.status_code >= 300:
        return error_result(f"Failed to fetch task comments: {response.status_code} {str(body)}")

    data = body.get("data", []) if isinstance(body, dict) else []
    pagination = body.get("pagination", {}) if isinstance(body, dict) else {}

    return ok_result({
        "task_id": task_id,
        "comments_count": len(data),
        "comments": data,
        "pagination": pagination,
    })
