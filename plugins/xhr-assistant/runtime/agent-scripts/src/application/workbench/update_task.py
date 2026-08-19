from __future__ import annotations

from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text, is_uuid
from src.shared.result import error_result, ok_result


PRIORITY_OPTIONS = ["Low", "Medium", "High", "Urgent"]


def _normalize_update_args(task_args: dict[str, Any]) -> dict[str, Any]:
    task_args = task_args if isinstance(task_args, dict) else {}

    description = task_args.get("description")
    if isinstance(description, str):
        description = description.strip() or None
    else:
        description = None

    story_point = task_args.get("story_point") if task_args.get("story_point") is not None else task_args.get("storyPoint") if task_args.get("storyPoint") is not None else task_args.get("story_points")
    if story_point is not None:
        try:
            story_point = int(story_point)
        except (ValueError, TypeError):
            story_point = None

    return {
        "task_id": clean_text(task_args.get("task_id") or task_args.get("taskId") or task_args.get("id")),
        "task_name": clean_text(task_args.get("task_name") or task_args.get("taskName") or task_args.get("name")),
        "description": description,
        "status_id": clean_text(task_args.get("status_id") or task_args.get("statusId") or task_args.get("status")),
        "priority": clean_text(task_args.get("priority")),
        "assignee_id": clean_text(task_args.get("assignee_id") or task_args.get("assigneeId") or task_args.get("assignee")),
        "reporter_id": clean_text(task_args.get("reporter_id") or task_args.get("reporterId") or task_args.get("reporter")),
        "start_date": clean_text(task_args.get("start_date") or task_args.get("startDate")),
        "due_date": clean_text(task_args.get("due_date") or task_args.get("dueDate") or task_args.get("end_date") or task_args.get("endDate")),
        "project_id": clean_text(task_args.get("project_id") or task_args.get("projectId")),
        "sprint_id": clean_text(task_args.get("sprint_id") or task_args.get("sprintId")),
        "story_point": story_point,
    }


async def run(task_args: Any, context: RequestContext, http_client: HttpClient) -> dict[str, Any]:
    api_base_url = context.api_base_url
    headers = context.headers

    args = _normalize_update_args(task_args)
    task_id = args["task_id"]

    if not task_id:
        return error_result("task_id is required")
    if not is_uuid(task_id):
        return error_result("task_id must be a valid UUID")

    payload: dict[str, Any] = {}
    if args["task_name"] is not None:
        payload["name"] = args["task_name"]
    if args["description"] is not None:
        payload["description"] = args["description"]
    if args["status_id"] is not None:
        if not is_uuid(args["status_id"]):
            return error_result("status_id must be a valid UUID")
        payload["status_id"] = args["status_id"]
        payload["statusId"] = args["status_id"]
    if args["priority"] is not None:
        matched_priority = next(
            (p for p in PRIORITY_OPTIONS if p.lower() == args["priority"].lower()),
            None,
        )
        if not matched_priority:
            return error_result(f"priority must be one of: {', '.join(PRIORITY_OPTIONS)}")
        payload["priority"] = matched_priority
    if args["assignee_id"] is not None:
        if args["assignee_id"] and not is_uuid(args["assignee_id"]):
            return error_result("assignee_id must be a valid UUID")
        val = args["assignee_id"] if args["assignee_id"] else None
        payload["assignee_id"] = val
        payload["assigneeId"] = val
    if args["reporter_id"] is not None:
        if args["reporter_id"] and not is_uuid(args["reporter_id"]):
            return error_result("reporter_id must be a valid UUID")
        val = args["reporter_id"] if args["reporter_id"] else None
        payload["reporter_id"] = val
        payload["reporterId"] = val
    if args["start_date"] is not None:
        payload["start_date"] = args["start_date"]
        payload["startDate"] = args["start_date"]
    if args["due_date"] is not None:
        payload["due_date"] = args["due_date"]
        payload["dueDate"] = args["due_date"]
    if args["project_id"] is not None:
        if not is_uuid(args["project_id"]):
            return error_result("project_id must be a valid UUID")
        payload["project_id"] = args["project_id"]
        payload["projectId"] = args["project_id"]
    if args["sprint_id"] is not None:
        val = args["sprint_id"] if args["sprint_id"] else None
        payload["sprint_id"] = val
        payload["sprintId"] = val
    if args["story_point"] is not None:
        payload["story_point"] = args["story_point"]
        payload["storyPoint"] = args["story_point"]

    if not payload:
        return error_result("At least one field to update must be provided")

    url = f"{api_base_url}/v1/pm/tasks/{task_id}"

    async with http_client.session() as client:
        response = await client.put(url, json=payload, headers=headers)

    try:
        body = response.json()
    except Exception:
        body = {"message": response.text}

    success = 200 <= response.status_code < 300
    if not success:
        return error_result(f"Task update failed: {response.status_code} {str(body)}")

    return ok_result({
        "task_id": task_id,
        "updated_fields": list(payload.keys()),
        "data": body.get("data") if isinstance(body, dict) and "data" in body else body,
    })
