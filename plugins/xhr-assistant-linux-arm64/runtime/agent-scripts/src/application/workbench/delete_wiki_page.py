from __future__ import annotations

from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text, is_uuid, to_bool
from src.shared.result import error_result, ok_result


def _normalize_args(task_args: dict[str, Any]) -> dict[str, Any]:
    task_args = task_args if isinstance(task_args, dict) else {}
    return {
        "page_id": clean_text(task_args.get("page_id") or task_args.get("pageId") or task_args.get("id")),
        "title": clean_text(task_args.get("title") or task_args.get("page_title")),
        "project_id": clean_text(task_args.get("project_id") or task_args.get("projectId")),
        "project_name": clean_text(task_args.get("project_name") or task_args.get("projectName")),
        "confirmed": to_bool(task_args.get("confirmed")),
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
    title = args["title"]
    raw_project_id = args["project_id"]
    project_name = args["project_name"]
    confirmed = args["confirmed"]

    project_id = await _resolve_project_id(raw_project_id, project_name, api_base_url, headers, http_client)
    page_id, resolved_title = await _resolve_page_id(raw_page_id, title, project_id, api_base_url, headers, http_client)
    display_title = resolved_title or title or page_id

    if not page_id:
        return error_result("page_id or title is required to delete a wiki page")
    if not is_uuid(page_id):
        return error_result("page_id must be a valid UUID")
    if project_id and not is_uuid(project_id):
        return error_result("project_id must be a valid UUID when provided")

    if not confirmed:
        cmd = f'python skills/workbench/delete_wiki_page/scripts/delete_wiki_page.py --page-id "{page_id}"'
        if project_id:
            cmd += f' --project-id "{project_id}"'
        cmd += ' --confirmed true'
        return ok_result({
            "page_id": page_id,
            "title": display_title,
            "project_id": project_id,
            "confirmed": False,
            "next_action": f"Deleting a wiki page is permanent. Ask the user for explicit confirmation. On confirmation, execute: {cmd}",
        })

    if project_id:
        url = f"{api_base_url}/v1/pm/projects/{project_id}/wiki/pages/{page_id}"
        scope = "project"
    else:
        url = f"{api_base_url}/v1/pm/company-pages/{page_id}"
        scope = "company"

    async with http_client.session() as client:
        response = await client.delete(url, headers=headers)

    if response.status_code >= 300:
        try:
            body = response.json()
        except Exception:
            body = {"message": response.text}
        return error_result(f"Failed to delete wiki page: {response.status_code} {str(body)}")

    return ok_result({
        "scope": scope,
        "page_id": page_id,
        "project_id": project_id,
        "deleted": True,
        "action": "page_deleted",
    })