from __future__ import annotations

from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text, is_uuid, to_bool
from src.shared.result import error_result, ok_result


def _normalize_args(task_args: dict[str, Any]) -> dict[str, Any]:
    task_args = task_args if isinstance(task_args, dict) else {}
    enable_sprint_val = task_args.get("enable_sprint") if "enable_sprint" in task_args else task_args.get("enableSprint")
    enable_sprint = to_bool(enable_sprint_val) if enable_sprint_val is not None else None
    return {
        "project_id": clean_text(task_args.get("project_id") or task_args.get("projectId") or task_args.get("id")),
        "project_name": clean_text(task_args.get("project_name") or task_args.get("projectName") or task_args.get("name")),
        "description": task_args.get("description"),
        "status_id": clean_text(task_args.get("status_id") or task_args.get("statusId") or task_args.get("status")),
        "start_date": clean_text(task_args.get("start_date") or task_args.get("startDate")),
        "target_date": clean_text(task_args.get("target_date") or task_args.get("targetDate") or task_args.get("end_date") or task_args.get("endDate")),
        "icon": clean_text(task_args.get("icon")),
        "color": clean_text(task_args.get("color")),
        "enable_sprint": enable_sprint,
    }


async def run(task_args: Any, context: RequestContext, http_client: HttpClient) -> dict[str, Any]:
    api_base_url = context.api_base_url
    headers = context.headers

    args = _normalize_args(task_args)
    project_id = args["project_id"]

    if not project_id:
        return error_result("project_id is required")
    if not is_uuid(project_id):
        return error_result("project_id must be a valid UUID")

    payload: dict[str, Any] = {}
    if args["project_name"] is not None:
        payload["name"] = args["project_name"]
    if args["description"] is not None:
        payload["description"] = args["description"]
    if args["status_id"] is not None:
        if not is_uuid(args["status_id"]):
            return error_result("status_id must be a valid UUID")
        payload["status_id"] = args["status_id"]
        payload["statusId"] = args["status_id"]
    if args["start_date"] is not None:
        payload["start_date"] = args["start_date"]
        payload["startDate"] = args["start_date"]
    if args["target_date"] is not None:
        payload["target_date"] = args["target_date"]
        payload["targetDate"] = args["target_date"]
    if args["icon"] is not None:
        payload["icon"] = args["icon"]
    if args["color"] is not None:
        payload["color"] = args["color"]
    if args["enable_sprint"] is not None:
        payload["enable_sprint"] = args["enable_sprint"]
        payload["enableSprint"] = args["enable_sprint"]

    if not payload:
        return error_result("At least one project field to update must be provided")

    url = f"{api_base_url}/v1/pm/projects/{project_id}"

    async with http_client.session() as client:
        response = await client.put(url, json=payload, headers=headers)

    try:
        body = response.json()
    except Exception:
        body = {"message": response.text}

    if response.status_code >= 300:
        return error_result(f"Failed to update project: {response.status_code} {str(body)}")

    data = body.get("data") if isinstance(body, dict) and "data" in body else body

    return ok_result({
        "project_id": project_id,
        "updated_fields": list(payload.keys()),
        "action": "project_updated",
        "data": data,
    })
