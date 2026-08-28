from __future__ import annotations

from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text, is_uuid, to_bool
from src.shared.result import error_result, ok_result


def _normalize_args(task_args: dict[str, Any]) -> dict[str, Any]:
    task_args = task_args if isinstance(task_args, dict) else {}
    return {
        "task_id": clean_text(task_args.get("task_id") or task_args.get("taskId") or task_args.get("id")),
        "task_name": clean_text(task_args.get("task_name") or task_args.get("taskName") or task_args.get("name")),
        "confirmed": to_bool(task_args.get("confirmed")),
    }


async def _resolve_task_id(
    identifier: str | None,
    task_name: str | None,
    api_base_url: str,
    headers: dict[str, str],
    http_client: HttpClient,
) -> str | None:
    if identifier and is_uuid(identifier):
        return identifier

    query_term = task_name or identifier
    if not query_term:
        return identifier

    url = f"{api_base_url}/v1/pm/tasks"
    async with http_client.session() as client:
        params = {"name": query_term, "page_number": 0, "page_size": 20}
        resp = await client.get(url, params=params, headers=headers)
        if 200 <= resp.status_code < 300:
            try:
                body = resp.json()
                tasks = body.get("data", []) if isinstance(body, dict) else []
                if isinstance(tasks, list):
                    for t in tasks:
                        if isinstance(t, dict):
                            if (
                                str(t.get("id", "")).lower() == query_term.lower()
                                or str(t.get("task_number", "")).lower() == query_term.lower()
                                or str(t.get("name", "")).strip().lower() == query_term.strip().lower()
                            ):
                                return str(t.get("id"))
                    if len(tasks) == 1 and isinstance(tasks[0], dict) and tasks[0].get("id"):
                        return str(tasks[0].get("id"))
            except Exception:
                pass

        resp = await client.get(url, params={"page_number": 0, "page_size": 50}, headers=headers)
        if 200 <= resp.status_code < 300:
            try:
                body = resp.json()
                tasks = body.get("data", []) if isinstance(body, dict) else []
                if isinstance(tasks, list):
                    for t in tasks:
                        if isinstance(t, dict):
                            if (
                                str(t.get("id", "")).lower() == query_term.lower()
                                or str(t.get("task_number", "")).lower() == query_term.lower()
                                or str(t.get("name", "")).strip().lower() == query_term.strip().lower()
                            ):
                                return str(t.get("id"))
            except Exception:
                pass

    return identifier


async def run(task_args: Any, context: RequestContext, http_client: HttpClient) -> dict[str, Any]:
    api_base_url = context.api_base_url
    headers = context.headers

    args = _normalize_args(task_args)
    raw_task_id = args["task_id"]
    task_name = args["task_name"]
    confirmed = args["confirmed"]

    task_id = await _resolve_task_id(raw_task_id, task_name, api_base_url, headers, http_client)

    if not task_id:
        return error_result("task_id is required")
    if not is_uuid(task_id):
        return error_result("task_id must be a valid UUID or existing task name/number")

    if not confirmed:
        preview_cmd = f'python skills/workbench/delete_task/scripts/delete_task.py --task-id "{task_id}" --confirmed true'
        return ok_result({
            "task_id": task_id,
            "task_name": task_name,
            "confirmed": False,
            "next_action": f"Task deletion is permanent. Ask the user for explicit confirmation. On confirmation, execute: {preview_cmd}",
        })

    url = f"{api_base_url}/v1/pm/tasks/{task_id}"

    async with http_client.session() as client:
        response = await client.delete(url, headers=headers)

    success = 200 <= response.status_code < 300
    if not success:
        try:
            body = response.json()
        except Exception:
            body = {"message": response.text}
        return error_result(f"Task deletion failed: {response.status_code} {str(body)}")

    return ok_result({
        "task_id": task_id,
        "deleted": True,
        "next_action": "task_deleted",
    })
