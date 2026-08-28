from __future__ import annotations

from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_int, clean_text, is_uuid, to_bool
from src.shared.result import error_result, ok_result


def _normalize_args(task_args: dict[str, Any]) -> dict[str, Any]:
    task_args = task_args if isinstance(task_args, dict) else {}
    action = clean_text(task_args.get("action")) or "list"
    action = action.lower()
    if action in {"add", "favorite", "pin", "star", "create"}:
        normalized_action = "add"
    elif action in {"remove", "unfavorite", "unpin", "unstar", "delete"}:
        normalized_action = "remove"
    else:
        normalized_action = "list"

    page = clean_int(task_args.get("page") or task_args.get("page_number") or task_args.get("pageNumber")) or 0
    size = clean_int(task_args.get("size") or task_args.get("page_size") or task_args.get("pageSize")) or 20

    return {
        "action": normalized_action,
        "project_id": clean_text(task_args.get("project_id") or task_args.get("projectId") or task_args.get("id")),
        "project_name": clean_text(task_args.get("project_name") or task_args.get("projectName") or task_args.get("name")),
        "page": max(page, 0),
        "size": min(max(size, 1), 100),
        "confirmed": to_bool(task_args.get("confirmed")),
    }


def _format_favorite_project(project: dict[str, Any]) -> dict[str, Any]:
    owner = project.get("owner") or {}
    status = project.get("status") or {}

    return {
        "project_id": project.get("id"),
        "project_name": project.get("name"),
        "code": project.get("project_code"),
        "owner": owner.get("full_name") or owner.get("email"),
        "start_date": project.get("start_date"),
        "due_date": project.get("due_date"),
        "status": status.get("name") if isinstance(status, dict) else str(status) if status else None,
        "total_tasks": project.get("total_tasks", 0),
        "visibility": project.get("project_visibility"),
        "enable_sprint": project.get("enable_sprint", False),
        "favorite": True,
    }


async def _resolve_project_id(
    identifier: str | None,
    project_name: str | None,
    api_base_url: str,
    headers: dict[str, str],
    http_client: HttpClient,
) -> tuple[str | None, str | None]:
    url = f"{api_base_url}/v1/pm/projects/basic-info"
    async with http_client.session() as client:
        # If identifier is a UUID, verify it against existing projects first
        if identifier and is_uuid(identifier):
            resp = await client.get(url, params={"pageSize": 100}, headers=headers)
            if 200 <= resp.status_code < 300:
                try:
                    body = resp.json()
                    projects = body.get("data", []) if isinstance(body, dict) else []
                    if isinstance(projects, list):
                        for p in projects:
                            if isinstance(p, dict) and str(p.get("id", "")).lower() == identifier.lower():
                                return identifier, p.get("name")
                except Exception:
                    pass
            # If identifier wasn't found in projects list, but project_name is provided, search by project_name
            if not project_name:
                return identifier, None

        query_term = project_name or identifier
        if not query_term:
            return None, None

        # Search by name query
        resp = await client.get(url, params={"name": query_term, "pageSize": 20}, headers=headers)
        if 200 <= resp.status_code < 300:
            try:
                body = resp.json()
                projects = body.get("data", []) if isinstance(body, dict) else []
                if isinstance(projects, list):
                    for p in projects:
                        if isinstance(p, dict):
                            p_id = str(p.get("id", ""))
                            p_code = str(p.get("project_code", ""))
                            p_name = str(p.get("name", "")).strip()
                            if (
                                p_id.lower() == query_term.lower()
                                or p_code.lower() == query_term.lower()
                                or p_name.lower() == query_term.lower()
                            ):
                                return p_id, p_name
                    if len(projects) == 1 and isinstance(projects[0], dict) and projects[0].get("id"):
                        return str(projects[0].get("id")), projects[0].get("name")
            except Exception:
                pass

        # Fallback search across all projects
        resp = await client.get(url, params={"pageSize": 100}, headers=headers)
        if 200 <= resp.status_code < 300:
            try:
                body = resp.json()
                projects = body.get("data", []) if isinstance(body, dict) else []
                if isinstance(projects, list):
                    for p in projects:
                        if isinstance(p, dict):
                            p_id = str(p.get("id", ""))
                            p_code = str(p.get("project_code", ""))
                            p_name = str(p.get("name", "")).strip()
                            if (
                                p_id.lower() == query_term.lower()
                                or p_code.lower() == query_term.lower()
                                or p_name.lower() == query_term.lower()
                            ):
                                return p_id, p_name
            except Exception:
                pass

    return identifier, project_name


async def run(task_args: Any, context: RequestContext, http_client: HttpClient) -> dict[str, Any]:
    api_base_url = context.api_base_url
    headers = context.headers

    args = _normalize_args(task_args)
    action = args["action"]
    raw_project_id = args["project_id"]
    project_name = args["project_name"]
    page = args["page"]
    size = args["size"]
    confirmed = args["confirmed"]

    if action == "list":
        url = f"{api_base_url}/v1/pm/projects/favorites"
        async with http_client.session() as client:
            response = await client.get(url, params={"page": page, "size": size}, headers=headers)

        if response.status_code >= 300:
            try:
                body = response.json()
            except Exception:
                body = {"message": response.text}
            return error_result(f"Failed to fetch favorite projects: {response.status_code} {str(body)}")

        try:
            payload = response.json()
            raw_projects = payload.get("data", []) if isinstance(payload, dict) else []
            meta = payload.get("meta", {}) if isinstance(payload, dict) else {}
        except Exception:
            raw_projects = []
            meta = {}

        formatted_projects = [
            _format_favorite_project(p) for p in raw_projects if isinstance(p, dict)
        ]

        return ok_result({
            "favorite_projects": formatted_projects,
            "favorites_count": len(formatted_projects),
            "meta": meta,
        })

    # Action add or remove
    project_id, resolved_name = await _resolve_project_id(
        raw_project_id, project_name, api_base_url, headers, http_client
    )
    display_name = resolved_name or project_name or project_id or "Unknown Project"

    if not project_id:
        return error_result("project_id or project_name is required to manage favorite space")
    if not is_uuid(project_id):
        return error_result("project_id must be a valid UUID or existing project name")

    if not confirmed:
        preview_cmd = (
            f'python skills/workbench/manage_favorite_spaces/scripts/manage_favorite_spaces.py '
            f'--action {action} --project-id "{project_id}" --confirmed true'
        )
        action_verb = "add to favorites" if action == "add" else "remove from favorites"
        return ok_result({
            "project_id": project_id,
            "project_name": display_name,
            "action": action,
            "confirmed": False,
            "next_action": (
                f"Confirm before proceeding: Ask the user if they confirm to {action_verb} "
                f"project '{display_name}' ({project_id}). On confirmation, execute: {preview_cmd}"
            ),
        })

    url = f"{api_base_url}/v1/pm/projects/{project_id}/favorite"
    async with http_client.session() as client:
        if action == "add":
            response = await client.post(url, headers=headers)
        else:
            response = await client.delete(url, headers=headers)

    if response.status_code >= 300:
        try:
            body = response.json()
        except Exception:
            body = {"message": response.text}
        verb = "add project to favorites" if action == "add" else "remove project from favorites"
        return error_result(f"Failed to {verb}: {response.status_code} {str(body)}")

    return ok_result({
        "project_id": project_id,
        "project_name": display_name,
        "action": f"project_{'favorited' if action == 'add' else 'unfavorited'}",
        "favorite": (action == "add"),
    })