from datetime import datetime
from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.core.models.types import Header
from src.shared.normalize import get_nested_value, normalize_list, to_bool
from src.shared.workbench.status_filters import resolve_status_filters
from src.shared.result import ok_result, error_result

PRIORITY_VALUES = {"URGENT", "HIGH", "MEDIUM", "LOW"}


def _format_task_entry(task):
    if not isinstance(task, dict):
        return None
    return {
        "task_number": task.get("task_number"),
        "task_name": task.get("name"),
        "status": get_nested_value(task, ["status", "name"]),
        "priority": task.get("priority"),
        "start_date": task.get("start_date"),
        "due_date": task.get("due_date"),
        "reporter": get_nested_value(task, ["reporter", "full_name"]),
        "assignee": get_nested_value(task, ["assignee", "full_name"]),
    }


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    page_number = task_args.get("page_number")
    if page_number is None:
        page_number = task_args.get("pageNumber", 0)
    page_size = task_args.get("page_size")
    if page_size is None:
        page_size = task_args.get("pageSize", 10)
    try:
        page_number = int(page_number)
    except Exception:
        page_number = 0

    try:
        page_size = int(page_size)
    except Exception:
        page_size = 10

    page_number = max(page_number, 0)
    page_size = min(max(page_size, 1), 25)

    include_completed = False

    priority_values = []
    for item in normalize_list(task_args.get("priorities") or task_args.get("priority")):
        upper = item.upper()
        if upper in PRIORITY_VALUES:
            priority_values.append(upper)

    status_ids_filter = normalize_list(task_args.get("status_id") or task_args.get("statusIds"))
    status_keys_filter = [value.lower() for value in normalize_list(task_args.get("status_key") or task_args.get("statusKeys"))]
    status_names_filter = [value.lower() for value in normalize_list(task_args.get("status_name") or task_args.get("statusNames"))]

    assignee_ids = normalize_list(task_args.get("assignee_id") or task_args.get("assigneeIds") or task_args.get("assigneeId"))
    mine = task_args.get("mine")
    if mine is None:
        mine = task_args.get("isMine")
    mine = to_bool(mine)
    if mine and not assignee_ids:
        assignee_ids = normalize_list(context.request_headers.get(Header.X_EMPLOYEE_ID))

    tasks_url = f"{api_base_url}/v1/pm/tasks/basic-info"
    statuses_url = f"{api_base_url}/v1/pm/statuses"

    async with http_client.session() as client:
        statuses_response = await client.get(statuses_url, headers=headers)

        try:
            statuses_payload = statuses_response.json()
        except Exception:
            statuses_payload = {}

        if isinstance(statuses_payload, dict):
            statuses_data = statuses_payload.get("data", []) or []
        else:
            statuses_data = []

        (
            resolved_status_ids,
            resolved_status_details,
            available_statuses,
        ) = resolve_status_filters(
            statuses_data,
            include_completed=include_completed,
            requested_ids=status_ids_filter,
            requested_keys=status_keys_filter,
            requested_names=status_names_filter,
        )

        if statuses_response.status_code < 200 or statuses_response.status_code >= 300:
            return error_result(f"Task statuses request failed: {statuses_response.status_code} {str(statuses_payload)}",)

        if not resolved_status_ids:
            return ok_result({
                "tasks": [],
                "meta": {
                    "page_number": page_number,
                    "page_size": page_size,
                    "has_next": False,
                },
                "reason": "No task statuses available to query",
                "available_statuses": available_statuses,
            })

        current_date = datetime.now().date().isoformat()
        request_body = {
            "status_ids": resolved_status_ids,
            "page_size": page_size,
            "page_number": page_number,
            "due_date": {"less_than": current_date},
        }

        if priority_values:
            request_body["priorities"] = priority_values

        if assignee_ids:
            request_body["assignee_ids"] = assignee_ids

        response = await client.post(tasks_url, json=request_body, headers=headers)

        try:
            payload = response.json()
        except Exception:
            payload = {}

        if isinstance(payload, dict):
            tasks = payload.get("data", []) or []
            meta = payload.get("meta", None)
        else:
            tasks = []
            meta = None

    formatted_tasks = []
    for task in tasks:
        formatted = _format_task_entry(task)
        if formatted:
            formatted_tasks.append(formatted)

    if response.status_code < 200 or response.status_code >= 300:
        return error_result(f"Overdue tasks request failed: {response.status_code} {str(payload)}",)

    return ok_result({
        "tasks_count": len(formatted_tasks),
        "tasks": formatted_tasks,
        "meta": meta,
        "filters": {
            "page_number": page_number,
            "page_size": page_size,
            "include_completed": include_completed,
            "priorities": priority_values,
            "status_ids": resolved_status_ids,
            "assignee_ids": assignee_ids,
            "mine": mine,
        },
        "selected_statuses": resolved_status_details,
        "available_statuses": available_statuses,
    })
