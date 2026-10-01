from __future__ import annotations

from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text, is_uuid, to_bool
from src.shared.result import error_result, ok_result


def _normalize_args(task_args: dict[str, Any]) -> dict[str, Any]:
    task_args = task_args if isinstance(task_args, dict) else {}
    return {
        "project_id": clean_text(task_args.get("project_id") or task_args.get("projectId")),
        "include_metrics": to_bool(task_args.get("include_metrics") or task_args.get("includeMetrics")),
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

    url = f"{api_base_url}/v1/pm/projects/{project_id}/sprints"

    async with http_client.session() as client:
        response = await client.get(url, headers=headers)

    try:
        body = response.json()
    except Exception:
        body = {}

    if response.status_code >= 300:
        return error_result(f"Failed to fetch project sprints: {response.status_code} {str(body)}")

    sprints = body.get("data") if isinstance(body, dict) and "data" in body else body if isinstance(body, list) else []

    active_sprints = [s for s in sprints if isinstance(s, dict) and s.get("status") == "ACTIVE"]
    planned_sprints = [s for s in sprints if isinstance(s, dict) and s.get("status") in {"PLANNED", "PLANNING"}]
    completed_sprints = [s for s in sprints if isinstance(s, dict) and s.get("status") == "COMPLETED"]

    return ok_result({
        "project_id": project_id,
        "sprints_count": len(sprints),
        "active_sprints": active_sprints,
        "planned_sprints": planned_sprints,
        "completed_sprints": completed_sprints,
        "sprints": sprints,
    })
