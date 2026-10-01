from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.core.models.types import Header
from src.shared.normalize import clean_text, is_uuid
from src.shared.result import ok_result, error_result


REQUIRED_FIELDS = [
    "task_name (string)",
    "project_id (UUID: resolve via `show_project_overview` when only a project name is known)",
    "status (UUID: use `get_task_status_meta` when the valid task status is still unknown)",
]
OPTIONAL_FIELDS = ["priority", "assignee_id", "start_date", "end_date", "description"]
PRIORITY_OPTIONS = ["Low", "Medium", "High", "Urgent"]


def _normalize_task_args(task_args):
    task_args = task_args if isinstance(task_args, dict) else {}

    description = task_args.get("description")
    if isinstance(description, str):
        description = description.strip() or None
    else:
        description = None

    return {
        "task_name": clean_text(task_args.get("task_name") or task_args.get("taskName")),
        "project_id": clean_text(task_args.get("project_id") or task_args.get("projectId")),
        "project_name": clean_text(task_args.get("project_name") or task_args.get("projectName")),
        "status": clean_text(task_args.get("status")),
        "priority": clean_text(task_args.get("priority")),
        "assignee_id": clean_text(task_args.get("assignee_id") or task_args.get("assigneeId")),
        "assignee": clean_text(task_args.get("assignee") or task_args.get("assignee_name") or task_args.get("assigneeName")),
        "start_date": clean_text(task_args.get("start_date") or task_args.get("startDate")),
        "end_date": clean_text(task_args.get("end_date") or task_args.get("endDate") or task_args.get("due_date") or task_args.get("dueDate")),
        "description": description,
    }


def _build_command_preview(normalized_args):
    command_parts = [
        'python skills/workbench/create_task/scripts/create_task.py',
        f'--task-name "{normalized_args["task_name"]}"' if normalized_args["task_name"] else '--task-name "<required string>"',
        f'--project-id "{normalized_args["project_id"]}"' if normalized_args["project_id"] else '--project-id "<required UUID from show_project_overview.projects.project_id>"',
        f'--status "{normalized_args["status"]}"' if normalized_args["status"] else '--status "<required UUID from get_task_status_meta.task_statuses.status_id>"',
    ]

    if normalized_args["priority"]:
        command_parts.append(f'--priority "{normalized_args["priority"]}"')
    if normalized_args["assignee_id"]:
        command_parts.append(f'--assignee-id "{normalized_args["assignee_id"]}"')
    if normalized_args["start_date"]:
        command_parts.append(f'--start-date "{normalized_args["start_date"]}"')
    if normalized_args["end_date"]:
        command_parts.append(f'--end-date "{normalized_args["end_date"]}"')
    if normalized_args["description"]:
        command_parts.append(f'--description "{normalized_args["description"]}"')

    return " ".join(command_parts)


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers
    reporter_id = context.request_headers.get(Header.X_EMPLOYEE_ID)

    if not reporter_id:
        return error_result("Missing xhr-employee-id header for reporter_id",)

    normalized_args = _normalize_task_args(task_args)

    missing_fields = []
    if not normalized_args["task_name"]:
        missing_fields.append("task_name")
    if not normalized_args["project_id"]:
        missing_fields.append("project_id")
    if not normalized_args["status"]:
        missing_fields.append("status")

    project_lookup_required = bool(normalized_args["project_name"] and not normalized_args["project_id"])
    status_lookup_required = bool(normalized_args["status"] and not is_uuid(normalized_args["status"]))
    assignee_lookup_required = bool(normalized_args["assignee"] and not normalized_args["assignee_id"])

    validation_errors = []
    if normalized_args["project_id"] and not is_uuid(normalized_args["project_id"]):
        validation_errors.append("project_id must be a UUID")
    if normalized_args["status"] and not is_uuid(normalized_args["status"]):
        validation_errors.append("status must be a UUID")
    if normalized_args["assignee_id"] and not is_uuid(normalized_args["assignee_id"]):
        validation_errors.append("assignee_id must be a UUID when provided")
    if normalized_args["priority"] and normalized_args["priority"] not in PRIORITY_OPTIONS:
        validation_errors.append("priority must be one of: Low, Medium, High, Urgent")

    payload = {
        "name": normalized_args["task_name"],
        "description": normalized_args["description"],
        "priority": normalized_args["priority"],
        "status_id": normalized_args["status"],
        "start_date": normalized_args["start_date"],
        "due_date": normalized_args["end_date"],
        "project_id": normalized_args["project_id"],
        "assignee_id": normalized_args["assignee_id"],
        "reporter_id": reporter_id,
    }

    data = {
        "task_name": normalized_args["task_name"],
        "project_id": normalized_args["project_id"],
        "project_name": normalized_args["project_name"],
        "status": normalized_args["status"],
        "priority": normalized_args["priority"],
        "assignee_id": normalized_args["assignee_id"],
        "assignee": normalized_args["assignee"],
        "start_date": normalized_args["start_date"],
        "end_date": normalized_args["end_date"],
        "description": normalized_args["description"],
        "required_fields": REQUIRED_FIELDS,
        "optional_fields": OPTIONAL_FIELDS,
        "priority_options": PRIORITY_OPTIONS,
        "missing_fields": missing_fields,
        "project_lookup_required": project_lookup_required,
        "status_lookup_required": status_lookup_required or not normalized_args["status"],
        "assignee_lookup_required": assignee_lookup_required,
        "validation_errors": validation_errors,
    }

    if missing_fields or project_lookup_required or status_lookup_required or assignee_lookup_required or validation_errors:
        next_steps = []
        if missing_fields:
            next_steps.append(
                "Fill any missing required fields. Required fields are task_name, project_id, and a task status UUID."
            )
        if project_lookup_required:
            next_steps.append(
                "Call show_project_overview with the provided project_name to resolve the concrete project_id and keep candidate projects visible if the match is ambiguous."
            )
        elif "project_id" in missing_fields:
            next_steps.append(
                "If only a project name is known, call show_project_overview and replace project_name with the selected project_id before writing."
            )
        if not normalized_args["status"]:
            next_steps.append(
                "Call get_task_status_meta to show valid task statuses, then store the selected `status_id` in `status`."
            )
        elif status_lookup_required:
            next_steps.append(
                "The provided `status` is not a UUID. Call get_task_status_meta and replace it with the selected task `status_id`."
            )
        if assignee_lookup_required:
            next_steps.append(
                "Call skills/employee/search_employees/scripts/search_employees.py with the provided assignee name, then store the selected employee UUID in `assignee_id` before writing."
            )
        if validation_errors:
            next_steps.append("Fix validation errors before writing: " + "; ".join(validation_errors))
        next_steps.append(
            "Do not write yet. Summarize the final payload for the user, including omitted optional fields, and obtain explicit confirmation first."
        )
        next_steps.append(
            f'After explicit confirmation, call exec with: {{"command": "{_build_command_preview(normalized_args)}"}}'
        )

        return ok_result({
            "data": data,
            "next_action": " ".join(next_steps),
            "meta": None,
            "query": {
                "task_name": normalized_args["task_name"],
                "project_id": normalized_args["project_id"],
                "project_name": normalized_args["project_name"],
                "status": normalized_args["status"],
                "assignee": normalized_args["assignee"],
                "assignee_id": normalized_args["assignee_id"],
            },
        })

    tasks_url = f"{api_base_url}/v1/pm/tasks"

    async with http_client.session() as client:
        response = await client.post(tasks_url, json=payload, headers=headers)

    try:
        body = response.json()
    except Exception:
        body = {"message": response.text}

    success = 200 <= response.status_code < 300

    if not success:
        return error_result(f"Task creation failed: {response.status_code} {str(body)}",)

    return ok_result({
        "data": body,
        "next_action": "task_created",
        "meta": {"payload_sent": payload},
        "query": {"endpoint": tasks_url},
    })
