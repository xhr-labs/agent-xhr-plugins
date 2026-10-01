from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text, is_uuid, to_bool
from src.shared.result import ok_result, error_result


REQUIRED_FIELDS = [
    "project_name (string)",
    "status (UUID: use `get_project_status_meta` when the valid project status is still unknown)",
]
OPTIONAL_FIELDS = ["description", "start_date", "due_date", "enable_sprint (boolean)"]


def _normalize_task_args(task_args):
    task_args = task_args if isinstance(task_args, dict) else {}
    enable_sprint_val = task_args.get("enable_sprint") if "enable_sprint" in task_args else task_args.get("enableSprint")
    enable_sprint = to_bool(enable_sprint_val) if enable_sprint_val is not None else None

    return {
        "project_name": clean_text(task_args.get("project_name") or task_args.get("projectName")),
        "description": clean_text(task_args.get("description")),
        "start_date": clean_text(task_args.get("start_date") or task_args.get("startDate")),
        "due_date": clean_text(task_args.get("due_date") or task_args.get("dueDate")),
        "status": clean_text(task_args.get("status") or task_args.get("status_id") or task_args.get("statusId")),
        "enable_sprint": enable_sprint,
    }


def _build_command_preview(normalized_args):
    command_parts = [
        'python skills/workbench/create_project/scripts/create_project.py',
        f'--project-name "{normalized_args["project_name"]}"' if normalized_args["project_name"] else '--project-name "<required string>"',
        f'--status "{normalized_args["status"]}"' if normalized_args["status"] else '--status "<required UUID from get_project_status_meta.project_statuses.status_id>"',
    ]

    if normalized_args["description"]:
        command_parts.append(f'--description "{normalized_args["description"]}"')
    if normalized_args["start_date"]:
        command_parts.append(f'--start-date "{normalized_args["start_date"]}"')
    if normalized_args["due_date"]:
        command_parts.append(f'--due-date "{normalized_args["due_date"]}"')
    if normalized_args["enable_sprint"] is not None:
        command_parts.append(f'--enable-sprint {str(normalized_args["enable_sprint"]).lower()}')

    return " ".join(command_parts)


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    normalized_args = _normalize_task_args(task_args)
    payload = {
        "name": normalized_args["project_name"],
        "description": normalized_args["description"],
        "start_date": normalized_args["start_date"],
        "target_date": normalized_args["due_date"],
        "status_id": normalized_args["status"],
    }
    if normalized_args["enable_sprint"] is not None:
        payload["enable_sprint"] = normalized_args["enable_sprint"]
        payload["enableSprint"] = normalized_args["enable_sprint"]

    missing_fields = []
    if not normalized_args["project_name"]:
        missing_fields.append("project_name")
    if not normalized_args["status"]:
        missing_fields.append("status")

    status_lookup_required = bool(normalized_args["status"] and not is_uuid(normalized_args["status"]))

    data = {
        "project_name": normalized_args["project_name"],
        "description": normalized_args["description"],
        "start_date": normalized_args["start_date"],
        "due_date": normalized_args["due_date"],
        "status": normalized_args["status"],
        "required_fields": REQUIRED_FIELDS,
        "optional_fields": OPTIONAL_FIELDS,
        "missing_fields": missing_fields,
        "status_lookup_required": status_lookup_required or not normalized_args["status"],
    }

    if missing_fields or status_lookup_required:
        next_steps = []
        if missing_fields:
            next_steps.append(
                "Fill any missing required fields. Required fields are project_name and a project status UUID."
            )
        if not normalized_args["status"]:
            next_steps.append(
                "Call get_project_status_meta to show valid project statuses, then store the selected `status_id` in `status`."
            )
        elif status_lookup_required:
            next_steps.append(
                "The provided `status` is not a UUID. Call get_project_status_meta and replace it with the selected project `status_id`."
            )
        next_steps.append(
            "Do not write yet. Summarize the final payload for the user and obtain explicit confirmation first."
        )
        next_steps.append(
            f'After explicit confirmation, call exec with: {{"command": "{_build_command_preview(normalized_args)}"}}'
        )

        return ok_result({
            "data": data,
            "next_action": " ".join(next_steps),
            "meta": None,
            "query": {
                "project_name": normalized_args["project_name"],
                "status": normalized_args["status"],
            },
        })

    projects_url = f"{api_base_url}/v1/pm/projects"

    async with http_client.session() as client:
        response = await client.post(projects_url, json=payload, headers=headers)

    try:
        body = response.json()
    except Exception:
        body = {"message": response.text}

    success = 200 <= response.status_code < 300

    if not success:
        return error_result(f"Project creation failed: {response.status_code} {str(body)}",)

    return ok_result({
        "data": body,
        "next_action": "project_created",
        "meta": {"payload_sent": payload},
        "query": {"endpoint": projects_url},
    })
