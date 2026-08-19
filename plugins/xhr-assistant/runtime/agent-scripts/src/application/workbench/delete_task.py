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


async def run(task_args: Any, context: RequestContext, http_client: HttpClient) -> dict[str, Any]:
    api_base_url = context.api_base_url
    headers = context.headers

    args = _normalize_args(task_args)
    task_id = args["task_id"]
    task_name = args["task_name"]
    confirmed = args["confirmed"]

    if not task_id:
        return error_result("task_id is required")
    if not is_uuid(task_id):
        return error_result("task_id must be a valid UUID")

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
