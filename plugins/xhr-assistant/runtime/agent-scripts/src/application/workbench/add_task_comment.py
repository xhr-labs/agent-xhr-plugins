from __future__ import annotations

from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text, is_uuid
from src.shared.result import error_result, ok_result


def _normalize_args(task_args: dict[str, Any]) -> dict[str, Any]:
    task_args = task_args if isinstance(task_args, dict) else {}
    return {
        "task_id": clean_text(task_args.get("task_id") or task_args.get("taskId")),
        "content": clean_text(task_args.get("content") or task_args.get("comment") or task_args.get("message")),
        "document_ids": task_args.get("document_ids") or task_args.get("documentIds") or [],
    }


async def run(task_args: Any, context: RequestContext, http_client: HttpClient) -> dict[str, Any]:
    api_base_url = context.api_base_url
    headers = context.headers

    args = _normalize_args(task_args)
    task_id = args["task_id"]
    content = args["content"]
    document_ids = args["document_ids"] if isinstance(args["document_ids"], list) else [args["document_ids"]] if args["document_ids"] else []

    if not task_id:
        return error_result("task_id is required")
    if not is_uuid(task_id):
        return error_result("task_id must be a valid UUID")
    if not content and not document_ids:
        return error_result("content or document_ids must be provided to create a comment")

    url = f"{api_base_url}/v1/pm/task-comments"
    payload = {
        "taskId": task_id,
        "task_id": task_id,
        "content": content or "",
        "documentIds": document_ids,
        "document_ids": document_ids,
    }

    async with http_client.session() as client:
        response = await client.post(url, json=payload, headers=headers)

    try:
        body = response.json()
    except Exception:
        body = {"message": response.text}

    if response.status_code >= 300:
        return error_result(f"Failed to add task comment: {response.status_code} {str(body)}")

    return ok_result({
        "task_id": task_id,
        "action": "comment_added",
        "data": body.get("data") if isinstance(body, dict) and "data" in body else body,
    })
