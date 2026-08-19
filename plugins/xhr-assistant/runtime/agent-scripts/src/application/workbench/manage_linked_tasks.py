from __future__ import annotations

from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text, is_uuid
from src.shared.result import error_result, ok_result


VALID_LINK_TYPES = {
    "blocks": "BLOCKS",
    "is_blocked_by": "IS_BLOCKED_BY",
    "relates_to": "RELATES_TO",
    "blocked_by": "IS_BLOCKED_BY",
    "relates": "RELATES_TO",
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
        normalized_link_type = VALID_LINK_TYPES.get(key, raw_link_type.upper())

    return {
        "action": action,
        "task_id": clean_text(task_args.get("task_id") or task_args.get("taskId")),
        "target_task_id": clean_text(
            task_args.get("target_task_id")
            or task_args.get("targetTaskId")
            or task_args.get("linked_task_id")
            or task_args.get("linkedTaskId")
        ),
        "link_type": normalized_link_type,
    }


async def run(task_args: Any, context: RequestContext, http_client: HttpClient) -> dict[str, Any]:
    api_base_url = context.api_base_url
    headers = context.headers

    args = _normalize_args(task_args)
    action = args["action"]
    task_id = args["task_id"]
    target_task_id = args["target_task_id"]
    link_type = args["link_type"] or "RELATES_TO"

    if not task_id:
        return error_result("task_id is required")
    if not is_uuid(task_id):
        return error_result("task_id must be a valid UUID")

    if action in {"add", "link", "create"}:
        if not target_task_id:
            return error_result("target_task_id is required to link tasks")
        if not is_uuid(target_task_id):
            return error_result("target_task_id must be a valid UUID")
        if task_id == target_task_id:
            return error_result("Cannot link a task to itself")

        url = f"{api_base_url}/v1/pm/tasks/{task_id}/links"
        payload = [{
            "targetTaskId": target_task_id,
            "target_task_id": target_task_id,
            "linkType": link_type,
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
            return error_result("target_task_id is required to unlink tasks")
        if not is_uuid(target_task_id):
            return error_result("target_task_id must be a valid UUID")

        url = f"{api_base_url}/v1/pm/tasks/{task_id}/links/{target_task_id}"

        async with http_client.session() as client:
            response = await client.delete(url, headers=headers)

        if response.status_code >= 300:
            try:
                body = response.json()
            except Exception:
                body = {"message": response.text}
            return error_result(f"Failed to unlink tasks: {response.status_code} {str(body)}")

        return ok_result({
            "task_id": task_id,
            "target_task_id": target_task_id,
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
    links = data.get("outgoing", []) if isinstance(data, dict) else data if isinstance(data, list) else []

    return ok_result({
        "task_id": task_id,
        "links_count": len(links),
        "links": links,
        "raw": data,
    })
