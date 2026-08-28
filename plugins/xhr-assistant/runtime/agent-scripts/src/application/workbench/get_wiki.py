from __future__ import annotations

from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text, is_uuid
from src.shared.result import error_result, ok_result


def _normalize_args(task_args: dict[str, Any]) -> dict[str, Any]:
    task_args = task_args if isinstance(task_args, dict) else {}
    return {
        "page_id": clean_text(task_args.get("page_id") or task_args.get("pageId") or task_args.get("id")),
        "page_title": clean_text(task_args.get("page_title") or task_args.get("pageTitle") or task_args.get("title")),
        "project_id": clean_text(task_args.get("project_id") or task_args.get("projectId")),
        "project_name": clean_text(task_args.get("project_name") or task_args.get("projectName")),
        "scope": clean_text(task_args.get("scope") or "project").lower(),
    }


async def _resolve_project_id(
    identifier: str | None,
    project_name: str | None,
    api_base_url: str,
    headers: dict[str, str],
    http_client: HttpClient,
) -> tuple[str | None, str | None]:
    if identifier and identifier.lower() == "company":
        return "company", "Company Wiki"

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
                                return identifier, p.get("name")
                except Exception:
                    pass
            if not project_name:
                return identifier, None

        query_term = project_name or identifier
        if not query_term:
            return None, None

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


async def _resolve_page_id(
    page_id: str | None,
    page_title: str | None,
    project_id: str | None,
    api_base_url: str,
    headers: dict[str, str],
    http_client: HttpClient,
) -> tuple[str | None, str | None]:
    if page_id and is_uuid(page_id):
        return page_id, page_title

    query_term = page_title or page_id
    if not query_term:
        return None, None

    is_company = (not project_id or project_id == "company")
    hierarchy_url = (
        f"{api_base_url}/v1/pm/company-wiki/pages/hierarchy"
        if is_company
        else f"{api_base_url}/v1/pm/projects/{project_id}/wiki/pages/hierarchy"
    )

    async with http_client.session() as client:
        resp = await client.get(hierarchy_url, headers=headers)
        if 200 <= resp.status_code < 300:
            try:
                body = resp.json()
                pages = body.get("data", []) if isinstance(body, dict) else []
                
                def find_in_tree(nodes):
                    if not isinstance(nodes, list):
                        return None, None
                    for node in nodes:
                        if isinstance(node, dict):
                            n_id = str(node.get("id", ""))
                            n_title = str(node.get("title", "")).strip()
                            if n_id.lower() == query_term.lower() or n_title.lower() == query_term.lower():
                                return n_id, n_title
                            children = node.get("children", [])
                            res_id, res_title = find_in_tree(children)
                            if res_id:
                                return res_id, res_title
                    return None, None

                res_id, res_title = find_in_tree(pages)
                if res_id:
                    return res_id, res_title
            except Exception:
                pass

    return page_id, page_title


async def run(task_args: Any, context: RequestContext, http_client: HttpClient) -> dict[str, Any]:
    api_base_url = context.api_base_url
    headers = context.headers

    args = _normalize_args(task_args)
    raw_page_id = args["page_id"]
    page_title = args["page_title"]
    raw_project_id = args["project_id"]
    project_name = args["project_name"]
    scope = args["scope"]

    if scope == "company" or raw_project_id == "company":
        project_id = "company"
        display_project = "Company Wiki"
    else:
        project_id, resolved_proj_name = await _resolve_project_id(
            raw_project_id, project_name, api_base_url, headers, http_client
        )
        display_project = resolved_proj_name or project_name or project_id

    page_id, resolved_page_title = await _resolve_page_id(
        raw_page_id, page_title, project_id, api_base_url, headers, http_client
    )
    display_page = resolved_page_title or page_title or page_id

    if not page_id:
        return error_result("page_id or page_title is required to fetch wiki content")

    is_company = (not project_id or project_id == "company")
    url = (
        f"{api_base_url}/v1/pm/company-pages/{page_id}"
        if is_company
        else f"{api_base_url}/v1/pm/projects/{project_id}/wiki/pages/{page_id}"
    )

    async with http_client.session() as client:
        response = await client.get(url, headers=headers)

    try:
        payload = response.json()
    except Exception:
        payload = {}

    if response.status_code >= 300:
        return error_result(f"Failed to fetch wiki page content: {response.status_code} {str(payload)}")

    data = payload.get("data") if isinstance(payload, dict) else payload

    return ok_result({
        "data": {
            "page_id": data.get("id") if isinstance(data, dict) else page_id,
            "title": data.get("title") if isinstance(data, dict) else display_page,
            "content": data.get("content") if isinstance(data, dict) else "",
        },
        "project_id": project_id,
        "project_name": display_project,
        "page_id": page_id,
        "scope": "company" if is_company else "project",
    })