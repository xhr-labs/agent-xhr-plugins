from __future__ import annotations

from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text, is_uuid, to_bool
from src.shared.result import error_result, ok_result


def _normalize_args(task_args: dict[str, Any]) -> dict[str, Any]:
    task_args = task_args if isinstance(task_args, dict) else {}
    return {
        "page_id": clean_text(task_args.get("page_id") or task_args.get("pageId") or task_args.get("id")),
        "title": clean_text(task_args.get("title") or task_args.get("page_title")),
        "project_id": clean_text(task_args.get("project_id") or task_args.get("projectId")),
        "confirmed": to_bool(task_args.get("confirmed")),
    }


async def run(task_args: Any, context: RequestContext, http_client: HttpClient) -> dict[str, Any]:
    api_base_url = context.api_base_url
    headers = context.headers

    args = _normalize_args(task_args)
    page_id = args["page_id"]
    title = args["title"]
    project_id = args["project_id"]
    confirmed = args["confirmed"]

    if not page_id:
        return error_result("page_id is required")
    if not is_uuid(page_id):
        return error_result("page_id must be a valid UUID")
    if project_id and not is_uuid(project_id):
        return error_result("project_id must be a valid UUID when provided")

    if not confirmed:
        cmd = f'python skills/workbench/delete_wiki_page/scripts/delete_wiki_page.py --page-id "{page_id}"'
        if project_id:
            cmd += f' --project-id "{project_id}"'
        cmd += ' --confirmed true'
        return ok_result({
            "page_id": page_id,
            "title": title,
            "project_id": project_id,
            "confirmed": False,
            "next_action": f"Deleting a wiki page is permanent. Ask the user for explicit confirmation. On confirmation, execute: {cmd}",
        })

    if project_id:
        url = f"{api_base_url}/v1/pm/projects/{project_id}/wiki/pages/{page_id}"
        scope = "project"
    else:
        url = f"{api_base_url}/v1/pm/company-pages/{page_id}"
        scope = "company"

    async with http_client.session() as client:
        response = await client.delete(url, headers=headers)

    if response.status_code >= 300:
        try:
            body = response.json()
        except Exception:
            body = {"message": response.text}
        return error_result(f"Failed to delete wiki page: {response.status_code} {str(body)}")

    return ok_result({
        "scope": scope,
        "page_id": page_id,
        "project_id": project_id,
        "deleted": True,
        "action": "page_deleted",
    })
