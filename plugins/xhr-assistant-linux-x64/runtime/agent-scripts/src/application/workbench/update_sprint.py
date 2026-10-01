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
        "sprint_name": clean_text(task_args.get("sprint_name") or task_args.get("sprintName") or task_args.get("name")),
        "goal": clean_text(task_args.get("goal") or task_args.get("sprint_goal") or task_args.get("sprintGoal")),
        "start_date": clean_text(task_args.get("start_date") or task_args.get("startDate")),
        "end_date": clean_text(task_args.get("end_date") or task_args.get("endDate")),
        "duration": clean_text(task_args.get("duration")),
    }


async def run(task_args: Any, context: RequestContext, http_client: HttpClient) -> dict[str, Any]:
    api_base_url = context.api_base_url
    headers = context.headers

    args = _normalize_args(task_args)
    project_id = args["project_id"]
    sprint_id = args["sprint_id"]

    if not project_id:
        return error_result("project_id is required")
    if not is_uuid(project_id):
        return error_result("project_id must be a valid UUID")
    if not sprint_id:
        return error_result("sprint_id is required")
    if not is_uuid(sprint_id):
        return error_result("sprint_id must be a valid UUID")

    payload: dict[str, Any] = {}
    if args["sprint_name"] is not None:
        payload["name"] = args["sprint_name"]
    if args["goal"] is not None:
        payload["goal"] = args["goal"]
    if args["start_date"] is not None:
        payload["startDate"] = args["start_date"]
        payload["start_date"] = args["start_date"]
    if args["end_date"] is not None:
        payload["endDate"] = args["end_date"]
        payload["end_date"] = args["end_date"]
    if args["duration"] is not None:
        payload["duration"] = args["duration"]

    if not payload:
        return error_result("At least one field to update must be provided")

    url = f"{api_base_url}/v1/pm/projects/{project_id}/sprints/{sprint_id}"

    async with http_client.session() as client:
        response = await client.put(url, json=payload, headers=headers)

    try:
        body = response.json()
    except Exception:
        body = {"message": response.text}

    if response.status_code >= 300:
        return error_result(f"Failed to update sprint: {response.status_code} {str(body)}")

    data = body.get("data") if isinstance(body, dict) and "data" in body else body

    return ok_result({
        "project_id": project_id,
        "sprint_id": sprint_id,
        "updated_fields": list(payload.keys()),
        "action": "sprint_updated",
        "data": data,
    })
