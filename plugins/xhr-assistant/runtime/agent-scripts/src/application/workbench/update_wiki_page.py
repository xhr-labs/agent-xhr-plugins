from __future__ import annotations

from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text, is_uuid
from src.shared.result import error_result, ok_result


def _normalize_args(task_args: dict[str, Any]) -> dict[str, Any]:
    task_args = task_args if isinstance(task_args, dict) else {}
    return {
        "page_id": clean_text(task_args.get("page_id") or task_args.get("pageId") or task_args.get("id")),
        "title": clean_text(task_args.get("title") or task_args.get("page_title") or task_args.get("name")),
        "content": task_args.get("content"),
        "project_id": clean_text(task_args.get("project_id") or task_args.get("projectId")),
    }


async def run(task_args: Any, context: RequestContext, http_client: HttpClient) -> dict[str, Any]:
    api_base_url = context.api_base_url
    headers = context.headers

    args = _normalize_args(task_args)
    page_id = args["page_id"]
    title = args["title"]
    content = args["content"]
    project_id = args["project_id"]

    if not page_id:
        return error_result("page_id is required")
    if not is_uuid(page_id):
        return error_result("page_id must be a valid UUID")
    if project_id and not is_uuid(project_id):
        return error_result("project_id must be a valid UUID when provided")

    payload: dict[str, Any] = {}
    if title is not None:
        payload["title"] = title
    if content is not None:
        payload["content"] = content

    if not payload:
        return error_result("At least title or content must be provided to update wiki page")

    if project_id:
        url = f"{api_base_url}/v1/pm/projects/{project_id}/wiki/pages/{page_id}"
        scope = "project"
    else:
        url = f"{api_base_url}/v1/pm/company-pages/{page_id}"
        scope = "company"

    async with http_client.session() as client:
        response = await client.patch(url, json=payload, headers=headers)

    try:
        body = response.json()
    except Exception:
        body = {"message": response.text}

    if response.status_code >= 300:
        return error_result(f"Failed to update wiki page: {response.status_code} {str(body)}")

    data = body.get("data") if isinstance(body, dict) and "data" in body else body

    return ok_result({
        "scope": scope,
        "page_id": page_id,
        "project_id": project_id,
        "updated_fields": list(payload.keys()),
        "action": "page_updated",
        "data": data,
    })
