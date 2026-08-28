from __future__ import annotations

from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text, is_uuid
from src.shared.result import error_result, ok_result


def _normalize_args(task_args: dict[str, Any]) -> dict[str, Any]:
    task_args = task_args if isinstance(task_args, dict) else {}
    return {
        "title": clean_text(task_args.get("title") or task_args.get("page_title") or task_args.get("name")),
        "content": task_args.get("content") or "",
        "project_id": clean_text(task_args.get("project_id") or task_args.get("projectId")),
        "project_name": clean_text(task_args.get("project_name") or task_args.get("projectName")),
        "parent_id": clean_text(task_args.get("parent_id") or task_args.get("parentId") or task_args.get("parent_page_id")),
    }


async def _resolve_project_id(
    identifier: str | None,
    project_name: str | None,
    api_base_url: str,
    headers: dict[str, str],
    http_client: HttpClient,
) -> str | None:
    if not identifier and not project_name:
        return None

    url = f"{api_base_url}/v1/pm/projects/basic-info"
    async with http_client.session() as client:
        if identifier and is_uuid(identifier):
            resp = await client.get(url, params={"pageSize": 100}, headers=headers)
            if 200 <= resp.status_code < 300:
                try:
                    body = resp.json()
                    projects = body.get("data", []) if isinstance(body, dict) else []
                    if isinstance(projects, list):
                        for p in projects:
                            if isinstance(p, dict) and str(p.get("id", "")).lower() == identifier.lower():
                                return identifier
                except Exception:
                    pass
            if not project_name:
                return identifier

        query_term = project_name or identifier
        if not query_term:
            return identifier

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
                                return p_id
                    if len(projects) == 1 and isinstance(projects[0], dict) and projects[0].get("id"):
                        return str(projects[0].get("id"))
            except Exception:
                pass

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
                                return p_id
            except Exception:
                pass

    return identifier


async def run(task_args: Any, context: RequestContext, http_client: HttpClient) -> dict[str, Any]:
    api_base_url = context.api_base_url
    headers = context.headers

    args = _normalize_args(task_args)
    title = args["title"]
    content = args["content"]
    raw_project_id = args["project_id"]
    project_name = args["project_name"]
    parent_id = args["parent_id"]

    if not title:
        return error_result("title is required")

    project_id = await _resolve_project_id(raw_project_id, project_name, api_base_url, headers, http_client)

    if project_id and not is_uuid(project_id):
        return error_result("project_id must be a valid UUID when provided")
    if parent_id and not is_uuid(parent_id):
        return error_result("parent_id must be a valid UUID when provided")

    payload: dict[str, Any] = {
        "title": title,
        "content": content,
    }
    if parent_id:
        payload["parentId"] = parent_id
        payload["parent_id"] = parent_id

    if project_id:
        url = f"{api_base_url}/v1/pm/projects/{project_id}/wiki/pages"
        scope = "project"
    else:
        url = f"{api_base_url}/v1/pm/company-pages"
        scope = "company"

    async with http_client.session() as client:
        response = await client.post(url, json=payload, headers=headers)

    try:
        body = response.json()
    except Exception:
        body = {"message": response.text}

    if response.status_code >= 300:
        return error_result(f"Failed to create wiki page: {response.status_code} {str(body)}")

    data = body.get("data") if isinstance(body, dict) else body
    page_id = data.get("id") if isinstance(data, dict) else None

    return ok_result({
        "page_id": page_id,
        "title": title,
        "scope": scope,
        "project_id": project_id,
        "parent_id": parent_id,
        "created": True,
    })