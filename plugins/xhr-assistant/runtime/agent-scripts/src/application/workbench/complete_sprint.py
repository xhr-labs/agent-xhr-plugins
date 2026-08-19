from __future__ import annotations

from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text, is_uuid
from src.shared.result import error_result, ok_result


def _normalize_args(task_args: dict[str, Any]) -> dict[str, Any]:
    task_args = task_args if isinstance(task_args, dict) else {}
    return {
        "project_id": clean_text(task_args.get("project_id") or task_args.get("projectId")),
        "sprint_id": clean_text(task_args.get("sprint_id") or task_args.get("sprintId") or task_args.get("id")),
        "move_to_sprint_id": clean_text(
            task_args.get("move_to_sprint_id")
            or task_args.get("moveToSprintId")
            or task_args.get("next_sprint_id")
            or task_args.get("nextSprintId")
        ),
    }


async def run(task_args: Any, context: RequestContext, http_client: HttpClient) -> dict[str, Any]:
    api_base_url = context.api_base_url
    headers = context.headers

    args = _normalize_args(task_args)
    project_id = args["project_id"]
    sprint_id = args["sprint_id"]
    move_to_sprint_id = args["move_to_sprint_id"]

    if not project_id:
        return error_result("project_id is required")
    if not is_uuid(project_id):
        return error_result("project_id must be a valid UUID")
    if not sprint_id:
        return error_result("sprint_id is required")
    if not is_uuid(sprint_id):
        return error_result("sprint_id must be a valid UUID")
    if move_to_sprint_id and not is_uuid(move_to_sprint_id):
        return error_result("move_to_sprint_id must be a valid UUID if provided")

    payload: dict[str, Any] = {
        "move_to_sprint_id": move_to_sprint_id if move_to_sprint_id else None,
        "moveToSprintId": move_to_sprint_id if move_to_sprint_id else None,
    }

    url = f"{api_base_url}/v1/pm/projects/{project_id}/sprints/{sprint_id}/complete"

    async with http_client.session() as client:
        response = await client.post(url, json=payload, headers=headers)

    try:
        body = response.json()
    except Exception:
        body = {"message": response.text}

    if response.status_code >= 300:
        return error_result(f"Failed to complete sprint: {response.status_code} {str(body)}")

    data = body.get("data") if isinstance(body, dict) and "data" in body else body

    return ok_result({
        "project_id": project_id,
        "sprint_id": sprint_id,
        "status": "COMPLETED",
        "moved_incomplete_tasks_to": move_to_sprint_id or "BACKLOG",
        "action": "sprint_completed",
        "data": data,
    })
