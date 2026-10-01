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
        "parent_id": clean_text(task_args.get("parent_id") or task_args.get("parentId")),
        "prev_id": clean_text(task_args.get("prev_id") or task_args.get("prevId")),
        "next_id": clean_text(task_args.get("next_id") or task_args.get("nextId")),
        "project_id": clean_text(task_args.get("project_id") or task_args.get("projectId")),
    }


async def run(task_args: Any, context: RequestContext, http_client: HttpClient) -> dict[str, Any]:
    api_base_url = context.api_base_url
    headers = context.headers

    args = _normalize_args(task_args)
    page_id = args["page_id"]
    parent_id = args["parent_id"]
    prev_id = args["prev_id"]
    next_id = args["next_id"]
    project_id = args["project_id"]

    if not page_id:
        return error_result("page_id is required")
    if not is_uuid(page_id):
        return error_result("page_id must be a valid UUID")
    if project_id and not is_uuid(project_id):
        return error_result("project_id must be a valid UUID when provided")
    if parent_id and not is_uuid(parent_id):
        return error_result("parent_id must be a valid UUID when provided")

    payload: dict[str, Any] = {}
    if parent_id is not None:
        payload["parentId"] = parent_id
        payload["parent_id"] = parent_id
    if prev_id:
        payload["prevId"] = prev_id
        payload["prev_id"] = prev_id
    if next_id:
        payload["nextId"] = next_id
        payload["next_id"] = next_id

    if project_id:
        url = f"{api_base_url}/v1/pm/projects/{project_id}/wiki/pages/{page_id}/reorder"
        scope = "project"
    else:
        url = f"{api_base_url}/v1/pm/company-pages/{page_id}/reorder"
        scope = "company"

    async with http_client.session() as client:
        response = await client.post(url, json=payload, headers=headers)

    try:
        body = response.json()
    except Exception:
        body = {"message": response.text}

    if response.status_code >= 300:
        return error_result(f"Failed to move wiki page: {response.status_code} {str(body)}")

    data = body.get("data") if isinstance(body, dict) and "data" in body else body

    return ok_result({
        "scope": scope,
        "page_id": page_id,
        "project_id": project_id,
        "parent_id": parent_id,
        "action": "page_moved",
        "data": data,
    })
