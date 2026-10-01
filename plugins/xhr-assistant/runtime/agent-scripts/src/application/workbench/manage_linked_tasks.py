from __future__ import annotations

from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text, is_uuid
from src.shared.result import error_result, ok_result


VALID_LINK_TYPES: dict[str, str] = {
    "blocks": "blocks",
    "is_blocked_by": "depends_on",
    "blocked_by": "depends_on",
    "depends_on": "depends_on",
    "depends": "depends_on",
    "parent_of": "parent_of",
    "parent": "parent_of",
    "is_parent_of": "parent_of",
    "child_of": "child_of",
    "child": "child_of",
    "is_child_of": "child_of",
    "related_to": "related_to",
    "relates_to": "related_to",
    "related": "related_to",
    "relates": "related_to",
    "duplicate_of": "duplicate_of",
    "duplicates": "duplicate_of",
    "is_duplicate_of": "duplicate_of",
    "caused_by": "caused_by",
    "causes": "caused_by",
    "is_caused_by": "caused_by",
}


def _normalize_args(task_args: dict[str, Any]) -> dict[str, Any]:
    task_args = task_args if isinstance(task_args, dict) else {}
    action = clean_text(task_args.get("action") or "get").lower()

    raw_link_type = clean_text(
        task_args.get("relation_type")
        or task_args.get("relationType")
        or task_args.get("link_type")
        or task_args.get("linkType")
    )
    normalized_link_type = None
    if raw_link_type:
        key = raw_link_type.lower().replace("-", "_")
        normalized_link_type = VALID_LINK_TYPES.get(key, key)

    return {
        "action": action,
        "task_id": clean_text(task_args.get("task_id") or task_args.get("taskId")),
        "target_task_id": clean_text(
            task_args.get("target_task_id")
            or task_args.get("targetTaskId")
            or task_args.get("linked_task_id")
            or task_args.get("linkedTaskId")
            or task_args.get("link_id")
            or task_args.get("linkId")
        ),
        "link_type": normalized_link_type,
    }


async def _resolve_task_id(
    identifier: str | None,
    api_base_url: str,
    headers: dict[str, str],
    http_client: HttpClient,
) -> str | None:
    if not identifier:
        return None
    if is_uuid(identifier):
        return identifier

    url = f"{api_base_url}/v1/pm/tasks"
    async with http_client.session() as client:
        # First try search by name/keyword
        params = {"name": identifier, "page_number": 0, "page_size": 20}
        resp = await client.get(url, params=params, headers=headers)
        if 200 <= resp.status_code < 300:
            try:
                body = resp.json()
                tasks = body.get("data", []) if isinstance(body, dict) else []
                if isinstance(tasks, list):
                    for t in tasks:
                        if isinstance(t, dict):
                            if (
                                str(t.get("id", "")).lower() == identifier.lower()
                                or str(t.get("task_number", "")).lower() == identifier.lower()
                                or str(t.get("name", "")).strip().lower() == identifier.strip().lower()
                            ):
                                return str(t.get("id"))
                    if len(tasks) == 1 and isinstance(tasks[0], dict) and tasks[0].get("id"):
                        return str(tasks[0].get("id"))
            except Exception:
                pass

        # Fallback: scan page 0 for task_number match
        resp = await client.get(url, params={"page_number": 0, "page_size": 50}, headers=headers)
        if 200 <= resp.status_code < 300:
            try:
                body = resp.json()
                tasks = body.get("data", []) if isinstance(body, dict) else []
                if isinstance(tasks, list):
                    for t in tasks:
                        if isinstance(t, dict):
                            if (
                                str(t.get("id", "")).lower() == identifier.lower()
                                or str(t.get("task_number", "")).lower() == identifier.lower()
                                or str(t.get("name", "")).strip().lower() == identifier.strip().lower()
                            ):
                                return str(t.get("id"))
            except Exception:
                pass

    return identifier


async def run(task_args: Any, context: RequestContext, http_client: HttpClient) -> dict[str, Any]:
    api_base_url = context.api_base_url
    headers = context.headers

    args = _normalize_args(task_args)
    action = args["action"]
    raw_task_id = args["task_id"]
    raw_target_task_id = args["target_task_id"]
    link_type = args["link_type"] or "related_to"

    task_id = await _resolve_task_id(raw_task_id, api_base_url, headers, http_client)
    target_task_id = await _resolve_task_id(raw_target_task_id, api_base_url, headers, http_client)

    if not task_id:
        return error_result("task_id is required")
    if not is_uuid(task_id):
        return error_result("task_id must be a valid UUID or existing task name/number")

    if action in {"add", "link", "create"}:
        if not target_task_id:
            return error_result("target_task_id is required to link tasks")
        if not is_uuid(target_task_id):
            return error_result("target_task_id must be a valid UUID")
        if task_id == target_task_id:
            return error_result("Cannot link a task to itself")

        url = f"{api_base_url}/v1/pm/tasks/{task_id}/links"
        payload = [{
            "target_task_ids": [target_task_id],
            "link_type": link_type,
        }]

        async with http_client.session() as client:
            response = await client.post(url, json=payload, headers=headers)

        try:
            body = response.json()
        except Exception:
            body = {"message": response.text}

        if response.status_code >= 300:
            return error_result(f"Failed to link tasks: {response.status_code} {str(body)}")

        return ok_result({
            "task_id": task_id,
            "target_task_id": target_task_id,
            "link_type": link_type,
            "action": "linked",
            "data": body,
        })

    if action in {"delete", "unlink", "remove"}:
        if not target_task_id:
            return error_result("target_task_id or link_id is required to unlink tasks")
        if not is_uuid(target_task_id):
            return error_result("target_task_id must be a valid UUID")

        link_id_to_delete = target_task_id

        # First, try fetching existing links to resolve target_task_id to the actual link UUID
        get_url = f"{api_base_url}/v1/pm/tasks/{task_id}/links"
        async with http_client.session() as client:
            get_resp = await client.get(get_url, headers=headers)
            if 200 <= get_resp.status_code < 300:
                try:
                    resp_data = get_resp.json()
                    links_data = resp_data.get("data", {}) if isinstance(resp_data, dict) else {}
                    all_links: list[dict[str, Any]] = []
                    if isinstance(links_data, dict):
                        all_links.extend(links_data.get("outgoing", []) or [])
                        all_links.extend(links_data.get("incoming", []) or [])
                    elif isinstance(links_data, list):
                        all_links.extend(links_data)

                    for link in all_links:
                        if isinstance(link, dict):
                            if (
                                link.get("id") == target_task_id
                                or link.get("target_task_id") == target_task_id
                                or link.get("source_task_id") == target_task_id
                            ):
                                link_id_to_delete = link.get("id") or target_task_id
                                break
                except Exception:
                    pass

            delete_url = f"{api_base_url}/v1/pm/tasks/{task_id}/links/{link_id_to_delete}"
            response = await client.delete(delete_url, headers=headers)

        if response.status_code >= 300:
            try:
                body = response.json()
            except Exception:
                body = {"message": response.text}
            return error_result(f"Failed to unlink tasks: {response.status_code} {str(body)}")

        return ok_result({
            "task_id": task_id,
            "target_task_id": target_task_id,
            "link_id": link_id_to_delete,
            "action": "unlinked",
        })

    # Default: get links
    url = f"{api_base_url}/v1/pm/tasks/{task_id}/links"

    async with http_client.session() as client:
        response = await client.get(url, headers=headers)

    try:
        body = response.json()
    except Exception:
        body = {}

    if response.status_code >= 300:
        return error_result(f"Failed to fetch task links: {response.status_code} {str(body)}")

    data = body.get("data") if isinstance(body, dict) and "data" in body else body
    outgoing = data.get("outgoing", []) if isinstance(data, dict) else data if isinstance(data, list) else []
    incoming = data.get("incoming", []) if isinstance(data, dict) else []

    return ok_result({
        "task_id": task_id,
        "links_count": len(outgoing) + len(incoming),
        "outgoing": outgoing,
        "incoming": incoming,
        "raw": data,
    })
