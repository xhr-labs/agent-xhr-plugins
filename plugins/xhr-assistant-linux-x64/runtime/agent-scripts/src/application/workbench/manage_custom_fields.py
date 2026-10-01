from __future__ import annotations

from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text, is_uuid
from src.shared.result import error_result, ok_result


def _normalize_args(task_args: dict[str, Any]) -> dict[str, Any]:
    task_args = task_args if isinstance(task_args, dict) else {}
    action = clean_text(task_args.get("action") or "list").lower()
    return {
        "task_id": clean_text(task_args.get("task_id") or task_args.get("taskId")),
        "project_id": clean_text(task_args.get("project_id") or task_args.get("projectId")),
        "field_id": clean_text(task_args.get("field_id") or task_args.get("fieldId") or task_args.get("custom_field_id")),
        "value": task_args.get("value") or task_args.get("field_value"),
        "action": action,
    }


async def run(task_args: Any, context: RequestContext, http_client: HttpClient) -> dict[str, Any]:
    api_base_url = context.api_base_url
    headers = context.headers

    args = _normalize_args(task_args)
    task_id = args["task_id"]
    project_id = args["project_id"]
    field_id = args["field_id"]
    value = args["value"]
    action = args["action"]

    if action in {"set", "set_value", "save", "update"}:
        if not task_id:
            return error_result("task_id is required to set custom field value")
        if not is_uuid(task_id):
            return error_result("task_id must be a valid UUID")
        if not field_id:
            return error_result("field_id is required")
        if not is_uuid(field_id):
            return error_result("field_id must be a valid UUID")

        url = f"{api_base_url}/v1/pm/custom-fields/values"
        payload = {
            "resourceId": task_id,
            "resource_id": task_id,
            "customFieldId": field_id,
            "custom_field_id": field_id,
            "value": value,
        }

        async with http_client.session() as client:
            response = await client.post(url, json=payload, headers=headers)

        if response.status_code >= 300:
            try:
                body = response.json()
            except Exception:
                body = {"message": response.text}
            return error_result(f"Failed to set custom field value: {response.status_code} {str(body)}")

        return ok_result({
            "task_id": task_id,
            "field_id": field_id,
            "value": value,
            "action": "custom_field_value_set",
        })

    # Default: list custom fields
    url = f"{api_base_url}/v1/pm/custom-fields/with-values"
    params: dict[str, Any] = {
        "section": "PROJECT_TASK_DETAIL",
        "source": "WORK_BENCH",
    }
    if project_id:
        params["ownerId"] = project_id
    if task_id:
        params["resourceIdIn"] = [task_id]

    async with http_client.session() as client:
        response = await client.get(url, params=params, headers=headers)

    try:
        body = response.json()
    except Exception:
        body = {}

    fields = body.get("data", []) if isinstance(body, dict) else []
    active_fields = [f for f in fields if isinstance(f, dict) and not f.get("deleted")]

    return ok_result({
        "project_id": project_id,
        "task_id": task_id,
        "custom_fields_count": len(active_fields),
        "custom_fields": active_fields,
    })
