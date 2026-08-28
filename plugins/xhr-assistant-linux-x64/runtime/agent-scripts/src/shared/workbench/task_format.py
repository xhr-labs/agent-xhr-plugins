"""Shared task formatting for Workbench task flows.

Two shapes exist in the API: the basic-info list rows (summary only — no
description, priority, dates, or assignee) and the GET /v1/pm/tasks/{id}
detail record. Employee nodes also come in two shapes: flat and
{employee: {...}}.
"""

from src.shared.normalize import get_nested_value


def employee_field(node, field):
    """Read an employee attribute from both API shapes: flat and {employee: {...}}."""
    if not isinstance(node, dict):
        return None
    employee = node.get("employee") if isinstance(node.get("employee"), dict) else node
    return employee.get(field)


def format_task_entry(task):
    """Summary row shared by task lists."""
    if not isinstance(task, dict):
        return None
    return {
        "id": task.get("id"),
        "task_id": task.get("id"),
        "task_number": task.get("task_number"),
        "task_name": task.get("name"),
        "status": get_nested_value(task, ["status", "name"]),
        # status_id lets follow-up update_task calls skip the status lookup.
        "status_id": get_nested_value(task, ["status", "id"]),
        "status_key": get_nested_value(task, ["status", "translate_key"]),
        "project_id": get_nested_value(task, ["project", "id"]) or task.get("project_id"),
        "task_type": task.get("task_type"),
        "priority": task.get("priority"),
        "start_date": task.get("start_date"),
        "due_date": task.get("due_date"),
        "sprint_id": task.get("sprint_id"),
        "story_point": task.get("story_point"),
        "logged_time_minutes": task.get("logged_time_minutes"),
        "dependency_task_ids": task.get("dependency_task_ids"),
        "reporter": employee_field(task.get("reporter"), "full_name"),
        "reporter_id": employee_field(task.get("reporter"), "id"),
        "assignee": employee_field(task.get("assignee"), "full_name"),
        "assignee_id": employee_field(task.get("assignee"), "id"),
    }


def format_task_detail(task):
    """Full record from GET /v1/pm/tasks/{id} — the summary row plus the
    detail-only fields."""
    entry = format_task_entry(task)
    if entry is None:
        return None
    entry.update(
        {
            "description": task.get("description"),
            "created_at": task.get("created_at"),
            "updated_at": task.get("updated_at"),
            "task_links": task.get("task_links"),
            "custom_fields": task.get("custom_fields"),
            "documents": task.get("documents"),
        }
    )
    return entry
