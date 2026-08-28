from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.core.models.types import Header
from src.shared.normalize import normalize_list, to_bool
from src.shared.workbench.status_filters import resolve_status_filters
from src.shared.workbench.task_format import format_task_detail, format_task_entry
from src.shared.result import ok_result, error_result

PRIORITY_VALUES = {"URGENT", "HIGH", "MEDIUM", "LOW"}


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    recursive = task_args.get("recursive")
    if recursive is None:
        recursive = task_args.get("isRecursive")
    recursive = bool(recursive) if isinstance(recursive, bool) else str(recursive).strip().lower() in {"1", "true", "yes", "y", "on"}

    page_number = task_args.get("page_number")
    if page_number is None:
        page_number = task_args.get("pageNumber", 0)
    page_size = task_args.get("page_size")
    if page_size is None:
        page_size = task_args.get("pageSize")
    if page_size is None:
        page_size = 1000 if recursive else 10
    try:
        page_number = int(page_number)
    except Exception:
        page_number = 0

    try:
        page_size = int(page_size)
    except Exception:
        page_size = 10

    page_number = max(page_number, 0)
    page_size = min(max(page_size, 1), 1000)

    include_completed = to_bool(task_args.get("include_completed"))
    if "include_completed" not in task_args and "includeCompleted" in task_args:
        include_completed = to_bool(task_args.get("includeCompleted"))

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
    project_id = task_args.get("project_id") or task_args.get("projectId")
    name_filter = task_args.get("name")
    due_date_filter = task_args.get("due_date") or task_args.get("dueDate")

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

        base_request_body = {
            "status_ids": resolved_status_ids,
            "page_size": page_size,
            "page_number": page_number,
        }

        if priority_values:
            base_request_body["priorities"] = priority_values

        if assignee_ids:
            base_request_body["assignee_ids"] = assignee_ids
        if project_id:
            base_request_body["project_id"] = project_id
        if name_filter:
            base_request_body["name"] = name_filter
        if due_date_filter:
            base_request_body["due_date"] = due_date_filter

        all_tasks = []
        final_meta = None
        final_status_code = 200
        pages_fetched = 0
        current_page_number = page_number

        while True:
            request_body = {
                **base_request_body,
                "page_number": current_page_number,
                "page_size": page_size,
            }

            response = await client.post(tasks_url, json=request_body, headers=headers)

            try:
                payload = response.json()
            except Exception:
                payload = {}

            final_status_code = response.status_code
            pages_fetched += 1

            redirect_to = None
            if isinstance(payload, dict):
                data_value = payload.get("data")
                if isinstance(data_value, dict):
                    redirect_to = data_value.get("redirect_to")

            if redirect_to:
                detail_url = f"{api_base_url}/v1/pm/tasks/{redirect_to}"
                detail_response = await client.get(detail_url, headers=headers)
                try:
                    detail_payload = detail_response.json()
                except Exception:
                    detail_payload = {}

                if isinstance(detail_payload, dict):
                    task = detail_payload.get("data")
                    meta = detail_payload.get("meta")
                else:
                    task = None
                    meta = None

                formatted_task = format_task_detail(task)
                data_output = [formatted_task] if formatted_task else []
                detail_meta = meta if isinstance(meta, dict) else {}
                detail_meta = {
                    **detail_meta,
                    "pages_fetched": pages_fetched,
                    "total_items_returned": len(data_output),
                }

                if detail_response.status_code < 200 or detail_response.status_code >= 300:
                    return error_result(f"Task detail request failed: {detail_response.status_code} {str(detail_payload)}",)

                return ok_result({
                    "tasks_count": len(data_output),
                    "tasks": data_output,
                    "meta": detail_meta,
                    "filters": {
                        "page_number": page_number,
                        "page_size": page_size,
                        "recursive": recursive,
                        "include_completed": include_completed,
                        "priorities": priority_values,
                        "status_ids": resolved_status_ids,
                        "assignee_ids": assignee_ids,
                        "project_id": project_id,
                        "name": name_filter,
                        "due_date": due_date_filter,
                        "mine": mine,
                    },
                    "redirect_to": redirect_to,
                    "selected_statuses": resolved_status_details,
                    "available_statuses": available_statuses,
                })

            if isinstance(payload, dict):
                tasks = payload.get("data", []) or []
                meta = payload.get("meta", None)
            else:
                tasks = []
                meta = None

            if isinstance(tasks, list):
                all_tasks.extend(tasks)

            final_meta = meta
            has_next = False
            if isinstance(meta, dict):
                has_next = bool(meta.get("has_next"))

            if response.status_code >= 400 or not recursive or not has_next:
                break
            current_page_number += 1

    formatted_tasks = []
    for task in all_tasks:
        formatted = format_task_entry(task)
        if formatted:
            formatted_tasks.append(formatted)

    enriched_meta = final_meta if isinstance(final_meta, dict) else {}
    enriched_meta = {
        **enriched_meta,
        "pages_fetched": pages_fetched,
        "total_items_returned": len(formatted_tasks),
    }

    if final_status_code < 200 or final_status_code >= 300:
        return error_result(f"Tasks request failed: {final_status_code}",)

    return ok_result({
        "tasks_count": len(formatted_tasks),
        "tasks": formatted_tasks,
        "meta": enriched_meta,
        "filters": {
            "page_number": page_number,
            "page_size": page_size,
            "recursive": recursive,
            "include_completed": include_completed,
            "priorities": priority_values,
            "status_ids": resolved_status_ids,
            "assignee_ids": assignee_ids,
            "project_id": project_id,
            "name": name_filter,
            "due_date": due_date_filter,
            "mine": mine,
        },
        "selected_statuses": resolved_status_details,
        "available_statuses": available_statuses,
    })
