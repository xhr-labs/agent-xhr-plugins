from __future__ import annotations

from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text, is_uuid
from src.shared.result import error_result, ok_result


def _normalize_args(task_args: dict[str, Any]) -> dict[str, Any]:
    task_args = task_args if isinstance(task_args, dict) else {}
    return {
        "title": clean_text(task_args.get("title") or task_args.get("page_title") or task_args.get("name")),
        "content": task_args.get("content") or "",
        "project_id": clean_text(task_args.get("project_id") or task_args.get("projectId")),
        "parent_id": clean_text(task_args.get("parent_id") or task_args.get("parentId") or task_args.get("parent_page_id")),
    }


async def run(task_args: Any, context: RequestContext, http_client: HttpClient) -> dict[str, Any]:
    api_base_url = context.api_base_url
    headers = context.headers

    args = _normalize_args(task_args)
    title = args["title"]
    content = args["content"]
    project_id = args["project_id"]
    parent_id = args["parent_id"]

    if not title:
        return error_result("title is required")
    if project_id and not is_uuid(project_id):
        return error_result("project_id must be a valid UUID when provided")
    if parent_id and not is_uuid(parent_id):
        return error_result("parent_id must be a valid UUID when provided")

    payload: dict[str, Any] = {
        "title": title,
        "content": content,
    }
    if parent_id:
        payload["parentId"] = parent_id
        payload["parent_id"] = parent_id

    if project_id:
        url = f"{api_base_url}/v1/pm/projects/{project_id}/wiki/pages"
        scope = "project"
    else:
        url = f"{api_base_url}/v1/pm/company-pages"
        scope = "company"

    async with http_client.session() as client:
        response = await client.post(url, json=payload, headers=headers)

    try:
        body = response.json()
    except Exception:
        body = {"message": response.text}

    if response.status_code >= 300:
        return error_result(f"Failed to create wiki page: {response.status_code} {str(body)}")

    data = body.get("data") if isinstance(body, dict) and "data" in body else body

    return ok_result({
        "scope": scope,
        "project_id": project_id,
        "page_id": data.get("id") if isinstance(data, dict) else None,
        "title": title,
        "action": "page_created",
        "data": data,
    })
