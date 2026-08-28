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
    if action in {"reply", "add_comment", "comment", "respond", "answer"}:
        normalized_action = "reply"
    elif action in {"create", "create_thread", "new_thread", "add_thread"}:
        normalized_action = "create_thread"
    elif action in {"resolve", "unresolve"}:
        normalized_action = "resolve"
    elif action in {"delete", "remove"}:
        normalized_action = "delete"
    else:
        normalized_action = "list"

    resolved_flag = task_args.get("resolved")
    if resolved_flag is None:
        resolved_flag = False if action == "unresolve" else True
    else:
        resolved_flag = to_bool(resolved_flag)

    return {
        "action": normalized_action,
        "project_id": clean_text(task_args.get("project_id") or task_args.get("projectId")),
        "project_name": clean_text(task_args.get("project_name") or task_args.get("projectName")),
        "page_id": clean_text(task_args.get("page_id") or task_args.get("pageId")),
        "page_title": clean_text(task_args.get("page_title") or task_args.get("pageTitle") or task_args.get("title")),
        "thread_id": clean_text(task_args.get("thread_id") or task_args.get("threadId")),
        "comment_id": clean_text(task_args.get("comment_id") or task_args.get("commentId")),
        "content": clean_text(task_args.get("content") or task_args.get("message") or task_args.get("comment") or task_args.get("text")),
        "selected_text": clean_text(task_args.get("selected_text") or task_args.get("selectedText")),
        "from_pos": clean_int(task_args.get("from_pos") or task_args.get("from")) or 0,
        "to_pos": clean_int(task_args.get("to_pos") or task_args.get("to")) or 0,
        "resolved": resolved_flag,
        "scope": clean_text(task_args.get("scope") or "project").lower(),
        "confirmed": to_bool(task_args.get("confirmed")),
    }


def _format_comment_thread(thread: dict[str, Any]) -> dict[str, Any]:
    author = thread.get("author") or {}
    comments = thread.get("comments") or []
    formatted_comments = []
    for c in comments:
        if isinstance(c, dict):
            c_author = c.get("author") or {}
            formatted_comments.append({
                "comment_id": c.get("id"),
                "content": c.get("content"),
                "author": c_author.get("name") or c.get("created_by") or "Unknown",
                "created_at": c.get("created_at"),
                "edited": c.get("edited", False),
            })

    return {
        "thread_id": thread.get("id"),
        "page_id": thread.get("page_id") or thread.get("pageId"),
        "resolved": thread.get("resolved", False),
        "selected_text": thread.get("selected_text") or thread.get("selectedText"),
        "author": author.get("name") or thread.get("created_by") or "Unknown",
        "created_at": thread.get("created_at"),
        "comments_count": len(formatted_comments),
        "comments": formatted_comments,
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

    is_company = (project_id == "company")
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
    action = args["action"]
    raw_project_id = args["project_id"]
    project_name = args["project_name"]
    raw_page_id = args["page_id"]
    page_title = args["page_title"]
    thread_id = args["thread_id"]
    comment_id = args["comment_id"]
    content = args["content"]
    selected_text = args["selected_text"]
    from_pos = args["from_pos"]
    to_pos = args["to_pos"]
    resolved = args["resolved"]
    scope = args["scope"]
    confirmed = args["confirmed"]

    if scope == "company" or raw_project_id == "company":
        project_id = "company"
        display_project = "Company Wiki"
    else:
        project_id, resolved_proj_name = await _resolve_project_id(
            raw_project_id, project_name, api_base_url, headers, http_client
        )
        display_project = resolved_proj_name or project_name or project_id

    if not project_id:
        return error_result("project_id or project_name is required (or set scope to 'company')")

    page_id, resolved_page_title = await _resolve_page_id(
        raw_page_id, page_title, project_id, api_base_url, headers, http_client
    )
    display_page = resolved_page_title or page_title or page_id

    if not page_id:
        return error_result(f"Wiki page '{page_title or raw_page_id}' could not be found or resolved in {display_project}")

    is_company = (project_id == "company")
    page_base_path = (
        f"{api_base_url}/v1/pm/company-wiki/pages/{page_id}"
        if is_company
        else f"{api_base_url}/v1/pm/projects/{project_id}/wiki/pages/{page_id}"
    )

    if action == "list":
        url = f"{page_base_path}/comment-threads"
        async with http_client.session() as client:
            response = await client.get(url, headers=headers)

        if response.status_code >= 300:
            try:
                body = response.json()
            except Exception:
                body = {"message": response.text}
            return error_result(f"Failed to fetch wiki comment threads: {response.status_code} {str(body)}")

        try:
            payload = response.json()
            raw_threads = payload.get("data", []) if isinstance(payload, dict) else payload if isinstance(payload, list) else []
        except Exception:
            raw_threads = []

        formatted_threads = [
            _format_comment_thread(t) for t in raw_threads if isinstance(t, dict)
        ]

        return ok_result({
            "project_id": project_id,
            "project_name": display_project,
            "page_id": page_id,
            "page_title": display_page,
            "threads_count": len(formatted_threads),
            "threads": formatted_threads,
        })

    # Write actions: reply, create_thread, resolve, delete
    if action == "reply":
        if not thread_id:
            return error_result("thread_id is required to reply to a wiki comment thread")
        if not content:
            return error_result("content (comment text) is required to reply to a wiki comment thread")

        if not confirmed:
            preview_cmd = (
                f'python skills/workbench/manage_wiki_comments/scripts/manage_wiki_comments.py '
                f'--action reply --project-id "{project_id}" --page-id "{page_id}" '
                f'--thread-id "{thread_id}" --content "{content}" --confirmed true'
            )
            return ok_result({
                "project_id": project_id,
                "project_name": display_project,
                "page_id": page_id,
                "page_title": display_page,
                "thread_id": thread_id,
                "content": content,
                "action": "reply",
                "confirmed": False,
                "next_action": (
                    f"Confirm before proceeding: Ask the user if they confirm replying to wiki comment thread "
                    f"'{thread_id}' on page '{display_page}' with message: \"{content}\". On confirmation, execute: {preview_cmd}"
                ),
            })

        url = f"{page_base_path}/comment-threads/{thread_id}/comments"
        async with http_client.session() as client:
            response = await client.post(url, json={"content": content}, headers=headers)

        if response.status_code >= 300:
            try:
                body = response.json()
            except Exception:
                body = {"message": response.text}
            return error_result(f"Failed to reply to wiki comment thread: {response.status_code} {str(body)}")

        try:
            res_data = response.json().get("data", {}) if isinstance(response.json(), dict) else {}
        except Exception:
            res_data = {}

        return ok_result({
            "project_id": project_id,
            "project_name": display_project,
            "page_id": page_id,
            "page_title": display_page,
            "thread_id": thread_id,
            "comment_id": res_data.get("id"),
            "content": content,
            "action": "comment_replied",
        })

    elif action == "create_thread":
        if not content:
            return error_result("content (comment text) is required to create a wiki comment thread")

        if not confirmed:
            preview_cmd = (
                f'python skills/workbench/manage_wiki_comments/scripts/manage_wiki_comments.py '
                f'--action create_thread --project-id "{project_id}" --page-id "{page_id}" '
                f'--content "{content}" --selected-text "{selected_text or ""}" --confirmed true'
            )
            return ok_result({
                "project_id": project_id,
                "project_name": display_project,
                "page_id": page_id,
                "page_title": display_page,
                "content": content,
                "selected_text": selected_text,
                "action": "create_thread",
                "confirmed": False,
                "next_action": (
                    f"Confirm before proceeding: Ask the user if they confirm creating a new comment thread on page "
                    f"'{display_page}' with message: \"{content}\". On confirmation, execute: {preview_cmd}"
                ),
            })

        url = f"{page_base_path}/comment-threads"
        body_payload = {
            "from": from_pos,
            "to": to_pos if to_pos > from_pos else from_pos + len(selected_text or ""),
            "selectedText": selected_text,
            "content": content,
        }
        async with http_client.session() as client:
            response = await client.post(url, json=body_payload, headers=headers)

        if response.status_code >= 300:
            try:
                body = response.json()
            except Exception:
                body = {"message": response.text}
            return error_result(f"Failed to create wiki comment thread: {response.status_code} {str(body)}")

        try:
            res_data = response.json().get("data", {}) if isinstance(response.json(), dict) else {}
        except Exception:
            res_data = {}

        return ok_result({
            "project_id": project_id,
            "project_name": display_project,
            "page_id": page_id,
            "page_title": display_page,
            "thread_id": res_data.get("id"),
            "action": "thread_created",
            "content": content,
        })

    elif action == "resolve":
        if not thread_id:
            return error_result("thread_id is required to resolve a wiki comment thread")

        if not confirmed:
            action_label = "resolve" if resolved else "unresolve"
            preview_cmd = (
                f'python skills/workbench/manage_wiki_comments/scripts/manage_wiki_comments.py '
                f'--action resolve --project-id "{project_id}" --page-id "{page_id}" '
                f'--thread-id "{thread_id}" --resolved {str(resolved).lower()} --confirmed true'
            )
            return ok_result({
                "project_id": project_id,
                "project_name": display_project,
                "page_id": page_id,
                "page_title": display_page,
                "thread_id": thread_id,
                "resolved": resolved,
                "action": "resolve",
                "confirmed": False,
                "next_action": (
                    f"Confirm before proceeding: Ask the user if they confirm marking thread '{thread_id}' "
                    f"as {action_label}d on page '{display_page}'. On confirmation, execute: {preview_cmd}"
                ),
            })

        url = f"{page_base_path}/comment-threads/{thread_id}"
        async with http_client.session() as client:
            response = await client.patch(url, json={"resolved": resolved}, headers=headers)

        if response.status_code >= 300:
            try:
                body = response.json()
            except Exception:
                body = {"message": response.text}
            return error_result(f"Failed to update wiki comment thread status: {response.status_code} {str(body)}")

        return ok_result({
            "project_id": project_id,
            "project_name": display_project,
            "page_id": page_id,
            "page_title": display_page,
            "thread_id": thread_id,
            "resolved": resolved,
            "action": "thread_status_updated",
        })

    elif action == "delete":
        if not comment_id:
            return error_result("comment_id is required to delete a wiki comment")

        if not confirmed:
            preview_cmd = (
                f'python skills/workbench/manage_wiki_comments/scripts/manage_wiki_comments.py '
                f'--action delete --project-id "{project_id}" --page-id "{page_id}" '
                f'--comment-id "{comment_id}" --confirmed true'
            )
            return ok_result({
                "project_id": project_id,
                "project_name": display_project,
                "page_id": page_id,
                "page_title": display_page,
                "comment_id": comment_id,
                "action": "delete",
                "confirmed": False,
                "next_action": (
                    f"Confirm before proceeding: Ask the user if they confirm permanently deleting wiki comment "
                    f"'{comment_id}' on page '{display_page}'. On confirmation, execute: {preview_cmd}"
                ),
            })

        url = f"{page_base_path}/comments/{comment_id}"
        async with http_client.session() as client:
            response = await client.delete(url, headers=headers)

        if response.status_code >= 300:
            try:
                body = response.json()
            except Exception:
                body = {"message": response.text}
            return error_result(f"Failed to delete wiki comment: {response.status_code} {str(body)}")

        return ok_result({
            "project_id": project_id,
            "project_name": display_project,
            "page_id": page_id,
            "page_title": display_page,
            "comment_id": comment_id,
            "action": "comment_deleted",
        })

    return error_result(f"Unknown action: {action}")