from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import normalize_list
from src.shared.result import ok_result, error_result


def _format_activity(activity):
    if not isinstance(activity, dict):
        return None
    task_id = activity.get("id")
    if not task_id:
        return None
    detail = activity.get("detail") or {}
    if not isinstance(detail, dict):
        detail = {}
    return {
        "task_id": task_id,
        "status": detail.get("new_value"),
        "updated_at": activity.get("created_at"),
    }


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    args = task_args
    if "task_id" in args and "taskId" not in args:
        args["taskId"] = args.get("task_id")
    if "task_ids" in args and "taskIds" not in args:
        args["taskIds"] = args.get("task_ids")
    task_ids = normalize_list(task_args.get("taskIds") or task_args.get("taskId"))
    activities_url = f"{api_base_url}/v1/pm/task-activities"

    async with http_client.session() as client:
        results = []
        status_codes = []

        for task_id in task_ids:
            params = {
                "taskId": task_id,
                "action": "UPDATED_STATUS",
                "sortDirection": "createdAt",
                "descSortDirection": "true",
                "size": 1,
            }
            response = await client.get(activities_url, headers=headers, params=params)
            status_codes.append(response.status_code)

            try:
                payload = response.json()
            except Exception:
                payload = {}

            activities = []
            if isinstance(payload, dict):
                data_value = payload.get("data")
                if isinstance(data_value, list):
                    activities = data_value
                elif isinstance(data_value, dict):
                    activities = [data_value]
            elif isinstance(payload, list):
                activities = payload

            if not activities:
                continue

            formatted = _format_activity(activities[0])
            if formatted:
                results.append(formatted)

    overall_status = 200 if status_codes and all(code == 200 for code in status_codes) else (status_codes[0] if status_codes else 200)

    if overall_status < 200 or overall_status >= 300:
        return error_result(f"Status latest request failed: {overall_status}",)

    return ok_result({
        "items_count": len(results),
        "items": results,
    })


