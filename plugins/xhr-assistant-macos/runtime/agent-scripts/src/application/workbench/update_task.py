from __future__ import annotations

from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text, is_uuid
from src.shared.result import error_result, ok_result
from src.shared.workbench.status_filters import is_task_status


PRIORITY_OPTIONS = ["Low", "Medium", "High", "Urgent"]


def _describe_statuses(statuses: list) -> str:
    return ", ".join(
        f"{status.get('name')} ({status.get('id')})" for status in statuses
    )


async def _fetch_task_statuses(client, api_base_url: str, headers) -> tuple[int, list]:
    """Return (status_code, task-scope statuses) from /v1/pm/statuses."""
    response = await client.get(f"{api_base_url}/v1/pm/statuses", headers=headers)
    try:
        payload = response.json()
    except Exception:
        payload = {}
    data = payload.get("data") or [] if isinstance(payload, dict) else []
    return response.status_code, [status for status in data if is_task_status(status)]


def _match_status_by_name(statuses: list, requested_name: str) -> list:
    wanted = requested_name.strip().casefold()
    wanted_key = wanted.replace(" ", "_").replace("-", "_")
    matches = []
    for status in statuses:
        name = (status.get("name") or "").strip().casefold()
        key_suffix = (status.get("translate_key") or "").rsplit(".", 1)[-1].casefold()
        if wanted == name or wanted_key == key_suffix:
            matches.append(status)
    return matches


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
        "status_name": clean_text(task_args.get("status_name") or task_args.get("statusName")),
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

    status_id = args["status_id"]
    status_name = args["status_name"]
    if status_id and not is_uuid(status_id) and not status_name:
        # Callers regularly pass a display name through status/status_id;
        # resolve it by name instead of failing on UUID validation.
        status_name, status_id = status_id, None
    if status_id and status_name:
        return error_result("Provide status_id or status_name, not both.")

    payload: dict[str, Any] = {}
    if args["task_name"] is not None:
        payload["name"] = args["task_name"]
    if args["description"] is not None:
        payload["description"] = args["description"]
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

    if not payload and not status_id and not status_name:
        return error_result("At least one field to update must be provided")

    url = f"{api_base_url}/v1/pm/tasks/{task_id}"

    async with http_client.session() as client:
        resolved_status = None
        if status_name:
            meta_code, task_statuses = await _fetch_task_statuses(client, api_base_url, headers)
            if meta_code < 200 or meta_code >= 300 or not task_statuses:
                return error_result(
                    f"Could not resolve status_name '{status_name}': the task status "
                    f"metadata request failed ({meta_code})."
                )
            matches = _match_status_by_name(task_statuses, status_name)
            if not matches:
                return error_result(
                    f"No Workbench task status matches '{status_name}'. "
                    f"Valid task statuses: {_describe_statuses(task_statuses)}"
                )
            if len(matches) > 1:
                return error_result(
                    f"status_name '{status_name}' is ambiguous: "
                    f"{_describe_statuses(matches)}. Retry with an explicit status_id."
                )
            resolved_status = matches[0]
            status_id = resolved_status.get("id")
        elif status_id:
            meta_code, task_statuses = await _fetch_task_statuses(client, api_base_url, headers)
            # Validate only when metadata is available; a metadata outage must
            # not block an otherwise valid update.
            if 200 <= meta_code < 300 and task_statuses:
                known_ids = {status.get("id") for status in task_statuses}
                if status_id not in known_ids:
                    return error_result(
                        f"status_id {status_id} is not a Workbench task status "
                        "(project statuses share display names such as 'In Progress' "
                        "but are rejected by the task workflow). Valid task statuses: "
                        f"{_describe_statuses(task_statuses)}"
                    )

        if status_id:
            payload["status_id"] = status_id
            payload["statusId"] = status_id

        response = await client.put(url, json=payload, headers=headers)

    try:
        body = response.json()
    except Exception:
        body = {"message": response.text}

    success = 200 <= response.status_code < 300
    if not success:
        return error_result(f"Task update failed: {response.status_code} {str(body)}")

    result = {
        "task_id": task_id,
        "updated_fields": list(payload.keys()),
        "data": body.get("data") if isinstance(body, dict) and "data" in body else body,
    }
    if resolved_status is not None:
        result["resolved_status"] = {
            "id": resolved_status.get("id"),
            "name": resolved_status.get("name"),
        }
    return ok_result(result)
