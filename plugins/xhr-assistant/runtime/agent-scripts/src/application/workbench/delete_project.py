from __future__ import annotations

from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text, is_uuid, to_bool
from src.shared.result import error_result, ok_result


def _normalize_args(task_args: dict[str, Any]) -> dict[str, Any]:
    task_args = task_args if isinstance(task_args, dict) else {}
    return {
        "project_id": clean_text(task_args.get("project_id") or task_args.get("projectId") or task_args.get("id")),
        "project_name": clean_text(task_args.get("project_name") or task_args.get("projectName") or task_args.get("name")),
        "confirmed": to_bool(task_args.get("confirmed")),
    }


async def run(task_args: Any, context: RequestContext, http_client: HttpClient) -> dict[str, Any]:
    api_base_url = context.api_base_url
    headers = context.headers

    args = _normalize_args(task_args)
    project_id = args["project_id"]
    project_name = args["project_name"]
    confirmed = args["confirmed"]

    if not project_id:
        return error_result("project_id is required")
    if not is_uuid(project_id):
        return error_result("project_id must be a valid UUID")

    if not confirmed:
        cmd = f'python skills/workbench/delete_project/scripts/delete_project.py --project-id "{project_id}" --confirmed true'
        return ok_result({
            "project_id": project_id,
            "project_name": project_name,
            "confirmed": False,
            "next_action": f"Deleting a project deletes all associated tasks and wikis. Ask the user for explicit confirmation. On confirmation, execute: {cmd}",
        })

    url = f"{api_base_url}/v1/pm/projects/{project_id}"

    async with http_client.session() as client:
        response = await client.delete(url, headers=headers)

    if response.status_code >= 300:
        try:
            body = response.json()
        except Exception:
            body = {"message": response.text}
        return error_result(f"Failed to delete project: {response.status_code} {str(body)}")

    return ok_result({
        "project_id": project_id,
        "deleted": True,
        "action": "project_deleted",
    })
