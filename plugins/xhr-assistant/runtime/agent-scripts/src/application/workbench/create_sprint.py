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
    sprint_name = args["sprint_name"]
    goal = args["goal"]
    start_date = args["start_date"]
    end_date = args["end_date"]
    duration = args["duration"]

    if not project_id:
        return error_result("project_id is required")
    if not is_uuid(project_id):
        return error_result("project_id must be a valid UUID")
    if not sprint_name:
        return error_result("sprint_name is required")

    payload: dict[str, Any] = {"name": sprint_name}
    if goal:
        payload["goal"] = goal
    if start_date:
        payload["startDate"] = start_date
        payload["start_date"] = start_date
    if end_date:
        payload["endDate"] = end_date
        payload["end_date"] = end_date
    if duration:
        payload["duration"] = duration

    url = f"{api_base_url}/v1/pm/projects/{project_id}/sprints"

    async with http_client.session() as client:
        response = await client.post(url, json=payload, headers=headers)

    try:
        body = response.json()
    except Exception:
        body = {"message": response.text}

    if response.status_code >= 300:
        return error_result(f"Failed to create sprint: {response.status_code} {str(body)}")

    data = body.get("data") if isinstance(body, dict) and "data" in body else body

    return ok_result({
        "project_id": project_id,
        "sprint_name": sprint_name,
        "action": "sprint_created",
        "data": data,
    })
