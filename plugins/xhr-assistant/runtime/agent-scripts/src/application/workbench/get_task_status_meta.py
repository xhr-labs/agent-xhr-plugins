from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.result import ok_result, error_result


def _format_task_status(status):
    if not isinstance(status, dict):
        return None

    status_id = status.get("id")
    if not status_id:
        return None

    translate_key = status.get("translate_key")
    if not (isinstance(translate_key, str) and translate_key.startswith("status.task.")):
        return None

    return {
        "status_id": status_id,
        "status_name": status.get("name"),
        "status_key": translate_key,
        "status_type": status.get("status_type"),
        "total_tasks": status.get("total_tasks"),
    }


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    statuses_url = f"{api_base_url}/v1/pm/statuses"

    async with http_client.session() as client:
        response = await client.get(statuses_url, headers=headers)

        try:
            payload = response.json()
        except Exception:
            payload = {}

    if isinstance(payload, dict):
        statuses = payload.get("data") or []
        meta = payload.get("meta")
    else:
        statuses = []
        meta = None

    task_statuses = []
    for status in statuses:
        formatted = _format_task_status(status)
        if formatted:
            task_statuses.append(formatted)

    if response.status_code < 200 or response.status_code >= 300:
        return error_result(f"Task statuses request failed: {response.status_code} {str(payload)}",)

    return ok_result({
        "task_statuses_count": len(task_statuses),
        "task_statuses": task_statuses,
        "filters": {
            "scope": "task",
        },
        "meta": meta,
        "query": {"endpoint": statuses_url},
    })
