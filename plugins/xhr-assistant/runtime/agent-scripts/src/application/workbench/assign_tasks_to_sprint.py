from __future__ import annotations

from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text, is_uuid
from src.shared.result import error_result, ok_result


def _normalize_args(task_args: dict[str, Any]) -> dict[str, Any]:
    task_args = task_args if isinstance(task_args, dict) else {}
    action = clean_text(task_args.get("action") or "add").lower()
    raw_task_ids = (
        task_args.get("task_ids")
        or task_args.get("taskIds")
        or task_args.get("task_id")
        or task_args.get("taskId")
        or []
    )
    if isinstance(raw_task_ids, str):
        raw_task_ids = [t.strip() for t in raw_task_ids.split(",") if t.strip()]

    return {
        "project_id": clean_text(task_args.get("project_id") or task_args.get("projectId")),
        "sprint_id": clean_text(task_args.get("sprint_id") or task_args.get("sprintId")),
        "task_ids": raw_task_ids,
        "action": action,
    }


async def run(task_args: Any, context: RequestContext, http_client: HttpClient) -> dict[str, Any]:
    api_base_url = context.api_base_url
    headers = context.headers

    args = _normalize_args(task_args)
    project_id = args["project_id"]
    sprint_id = args["sprint_id"]
    task_ids = args["task_ids"]
    action = args["action"]

    if not project_id:
        return error_result("project_id is required")
    if not is_uuid(project_id):
        return error_result("project_id must be a valid UUID")
    if not sprint_id:
        return error_result("sprint_id is required")
    if not is_uuid(sprint_id):
        return error_result("sprint_id must be a valid UUID")
    if not task_ids:
        return error_result("At least one task_id must be provided")

    for tid in task_ids:
        if not is_uuid(tid):
            return error_result(f"Invalid task UUID: {tid}")

    is_remove = action in {"remove", "delete", "unlink", "backlog"}
    endpoint = f"{api_base_url}/v1/pm/projects/{project_id}/sprints/{sprint_id}/tasks"
    if is_remove:
        endpoint += "/remove"

    payload = {
        "task_ids": task_ids,
        "taskIds": task_ids,
    }

    async with http_client.session() as client:
        response = await client.post(endpoint, json=payload, headers=headers)

    try:
        body = response.json()
    except Exception:
        body = {"message": response.text}

    if response.status_code >= 300:
        return error_result(f"Failed to {'remove' if is_remove else 'assign'} tasks to sprint: {response.status_code} {str(body)}")

    data = body.get("data") if isinstance(body, dict) and "data" in body else body

    return ok_result({
        "project_id": project_id,
        "sprint_id": sprint_id,
        "task_ids": task_ids,
        "action": "tasks_removed_to_backlog" if is_remove else "tasks_assigned_to_sprint",
        "data": data,
    })
