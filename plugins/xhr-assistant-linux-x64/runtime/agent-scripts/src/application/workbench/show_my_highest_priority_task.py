from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.core.models.types import Header
from src.shared.normalize import normalize_list
from src.shared.result import ok_result, error_result

# Priority order from highest to lowest
PRIORITY_ORDER = ["URGENT", "HIGH", "MEDIUM", "LOW"]


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers
    employee_id = context.request_headers.get(Header.X_EMPLOYEE_ID)

    task_args = task_args if isinstance(task_args, dict) else {}
    page_size = 10
    page_number = task_args.get("page_number")
    if page_number is None:
        page_number = task_args.get("pageNumber", 0)

    tasks_url = f"{api_base_url}/v1/pm/tasks/basic-info"
    statuses_url = f"{api_base_url}/v1/pm/statuses"

    async with http_client.session() as client:
        statuses_response = await client.get(statuses_url, headers=headers)

        try:
            statuses_payload = statuses_response.json()
        except Exception:
            statuses_payload = {}

        if isinstance(statuses_payload, dict):
            statuses_data = statuses_payload.get("data", [])
        else:
            statuses_data = []

        status_ids = []
        for status in statuses_data:
            translate_key = status.get("translate_key") or ""
            if not translate_key.startswith("status.task"):
                continue

            last = translate_key.split(".")[-1].lower()
            if last in ["done", "completed"]:
                continue

            status_id = status.get("id")
            if status_id:
                status_ids.append(status_id)

        if statuses_response.status_code < 200 or statuses_response.status_code >= 300:
            return error_result(f"Statuses request failed: {statuses_response.status_code} {str(statuses_payload)}",)

        if not status_ids:
            return ok_result({
                "tasks": [],
                "meta": {"page_number": page_number, "page_size": page_size, "has_next": False},
                "reason": "No active statuses found",
            })

        last_status = None
        last_meta = None

        for priority in PRIORITY_ORDER:
            request_body = {
                "status_ids": normalize_list(status_ids),
                "priorities": normalize_list(priority),
                "page_size": page_size,
                "page_number": page_number,
            }

            assignee_ids = normalize_list(employee_id)
            if assignee_ids:
                request_body["assignee_ids"] = assignee_ids

            response = await client.post(tasks_url, json=request_body, headers=headers)
            last_status = response.status_code

            try:
                payload = response.json()
            except Exception:
                payload = None

            if isinstance(payload, dict):
                tasks = payload.get("data", []) or []
                meta = payload.get("meta", None)
            else:
                tasks = []
                meta = None

            last_meta = meta

            if last_status is not None and (last_status < 200 or last_status >= 300):
                return error_result(f"Tasks request failed: {last_status} {str(payload)}",)

            if tasks:
                return ok_result({
                    "priority": priority,
                    "tasks_count": len(tasks),
                    "tasks": tasks,
                    "meta": meta,
                })

        return ok_result({
            "priority": None,
            "tasks_count": 0,
            "tasks": [],
            "meta": last_meta,
            "reason": "No tasks found at any priority level",
        })
