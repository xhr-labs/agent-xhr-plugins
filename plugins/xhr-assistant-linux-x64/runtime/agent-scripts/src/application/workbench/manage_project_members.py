from __future__ import annotations

from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text, is_uuid
from src.shared.result import error_result, ok_result


VALID_ROLES = {"OWNER", "CONTRIBUTOR", "VIEWER", "MEMBER"}


def _normalize_args(task_args: dict[str, Any]) -> dict[str, Any]:
    task_args = task_args if isinstance(task_args, dict) else {}
    action = clean_text(task_args.get("action") or "list").lower()
    raw_role = clean_text(task_args.get("role") or task_args.get("share_role") or "CONTRIBUTOR").upper()
    if raw_role == "MEMBER":
        raw_role = "CONTRIBUTOR"

    return {
        "project_id": clean_text(task_args.get("project_id") or task_args.get("projectId")),
        "employee_id": clean_text(task_args.get("employee_id") or task_args.get("employeeId") or task_args.get("member_id")),
        "role": raw_role,
        "action": action,
    }


async def run(task_args: Any, context: RequestContext, http_client: HttpClient) -> dict[str, Any]:
    api_base_url = context.api_base_url
    headers = context.headers

    args = _normalize_args(task_args)
    project_id = args["project_id"]
    employee_id = args["employee_id"]
    role = args["role"]
    action = args["action"]

    if not project_id:
        return error_result("project_id is required")
    if not is_uuid(project_id):
        return error_result("project_id must be a valid UUID")

    if action in {"add", "invite", "create"}:
        if not employee_id:
            return error_result("employee_id is required to add member")
        if not is_uuid(employee_id):
            return error_result("employee_id must be a valid UUID")
        if role not in VALID_ROLES:
            return error_result("role must be OWNER, CONTRIBUTOR, or VIEWER")

        url = f"{api_base_url}/v1/pm/projects/{project_id}/employees"
        payload = [{"employee": {"id": employee_id}, "role": role}]

        async with http_client.session() as client:
            response = await client.post(url, json=payload, headers=headers)

        if response.status_code >= 300:
            try:
                body = response.json()
            except Exception:
                body = {"message": response.text}
            return error_result(f"Failed to add project member: {response.status_code} {str(body)}")

        return ok_result({
            "project_id": project_id,
            "employee_id": employee_id,
            "role": role,
            "action": "member_added",
        })

    if action in {"remove", "delete"}:
        if not employee_id:
            return error_result("employee_id is required to remove member")
        if not is_uuid(employee_id):
            return error_result("employee_id must be a valid UUID")

        url = f"{api_base_url}/v1/pm/projects/{project_id}/employees/{employee_id}"

        async with http_client.session() as client:
            response = await client.delete(url, headers=headers)

        if response.status_code >= 300:
            try:
                body = response.json()
            except Exception:
                body = {"message": response.text}
            return error_result(f"Failed to remove project member: {response.status_code} {str(body)}")

        return ok_result({
            "project_id": project_id,
            "employee_id": employee_id,
            "action": "member_removed",
        })

    if action in {"update_role", "change_role", "set_role"}:
        if not employee_id:
            return error_result("employee_id is required to update member role")
        if not is_uuid(employee_id):
            return error_result("employee_id must be a valid UUID")

        url = f"{api_base_url}/v1/pm/projects/{project_id}/employees/{employee_id}"
        payload = {"role": role}

        async with http_client.session() as client:
            response = await client.put(url, json=payload, headers=headers)

        if response.status_code >= 300:
            try:
                body = response.json()
            except Exception:
                body = {"message": response.text}
            return error_result(f"Failed to update member role: {response.status_code} {str(body)}")

        return ok_result({
            "project_id": project_id,
            "employee_id": employee_id,
            "role": role,
            "action": "role_updated",
        })

    # Default: list members
    url = f"{api_base_url}/v1/pm/projects/{project_id}/employees/by-name"

    async with http_client.session() as client:
        response = await client.get(url, params={"size": 100}, headers=headers)

    try:
        body = response.json()
    except Exception:
        body = {}

    if response.status_code >= 300:
        return error_result(f"Failed to list project members: {response.status_code} {str(body)}")

    members = body.get("data", []) if isinstance(body, dict) else []

    return ok_result({
        "project_id": project_id,
        "members_count": len(members),
        "members": members,
    })
