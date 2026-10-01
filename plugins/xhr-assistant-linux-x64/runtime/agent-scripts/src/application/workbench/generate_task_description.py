from __future__ import annotations

from typing import Any
import json

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text
from src.shared.result import error_result, ok_result


ACTION_NAME = "project_task_description_setup"


def _first_value(task_args: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in task_args and task_args[key] is not None:
            return task_args[key]
    return None


def _unwrap_description_value(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    trimmed = value.strip()
    if not trimmed.startswith("{") or not trimmed.endswith("}"):
        return value
    try:
        parsed = json.loads(trimmed)
    except Exception:
        return value
    if not isinstance(parsed, dict):
        return value
    for key in ("description", "task_description", "taskDescription", "content"):
        nested = parsed.get(key)
        if nested is not None:
            return nested
    return value


def _normalize_description_value(value: Any) -> Any:
    if not isinstance(value, str):
        return value

    normalized = value.strip()
    if not normalized:
        return normalized

    # If markdown markers are unbalanced and the string ends with a dangling
    # bold closer, trim the trailing marker rather than leaking malformed
    # markdown into the frontend field.
    if normalized.count("**") % 2 == 1 and normalized.endswith("**"):
        normalized = normalized[:-2].rstrip()

    # Sometimes the model wraps an entire multiline poem/list in a single
    # outer bold block. Keep inline emphasis, but remove that outer wrapper.
    if (
        "\n" in normalized
        and normalized.startswith("**")
        and normalized.endswith("**")
        and normalized.count("**") == 2
    ):
        normalized = normalized[2:-2].strip()

    return normalized


async def run(task_args, context: RequestContext, http_client: HttpClient):
    task_args = task_args if isinstance(task_args, dict) else {}

    description = clean_text(
        _normalize_description_value(
            _unwrap_description_value(
                _first_value(
                    task_args,
                    "description",
                    "task_description",
                    "taskDescription",
                    "content",
                )
            )
        )
    )

    if not description:
        return error_result("task_description_required")

    return ok_result(
        {
            "content": {
                "description": description,
            },
            "action": ACTION_NAME,
        }
    )
