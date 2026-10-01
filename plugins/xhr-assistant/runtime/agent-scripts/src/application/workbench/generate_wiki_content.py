from __future__ import annotations

from typing import Any
import json

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text
from src.shared.result import error_result, ok_result


DEFAULT_SLOT_ID = "generated-wiki-content"
DEFAULT_ACTION_LABEL = "Do you want to accept this version or try again?"
CLIENT_CONTEXT_DATA_HEADER = "x-agent-client-context-data"


def _first_value(task_args: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in task_args and task_args[key] is not None:
            return task_args[key]
    return None


def _unwrap_content_value(value: Any) -> Any:
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
    for key in ("content", "wiki_content", "wikiContent", "markdown", "description"):
        nested = parsed.get(key)
        if nested is not None:
            return nested
    return value


def _normalize_markdown_value(value: Any) -> Any:
    if not isinstance(value, str):
        return value

    normalized = value.strip()
    if not normalized:
        return normalized

    if normalized.count("```") % 2 == 0 and normalized.startswith("```") and normalized.endswith("```"):
        lines = normalized.splitlines()
        if len(lines) >= 2:
            normalized = "\n".join(lines[1:-1]).strip()

    return normalized


def _normalize_client_context_data(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return dict(value)
    if not isinstance(value, str):
        return {}

    trimmed = value.strip()
    if not trimmed:
        return {}
    try:
        parsed = json.loads(trimmed)
    except Exception:
        return {}
    return dict(parsed) if isinstance(parsed, dict) else {}


def _client_context_data(context: RequestContext) -> dict[str, Any]:
    request_headers = context.request_headers if isinstance(context.request_headers, dict) else {}
    return _normalize_client_context_data(request_headers.get(CLIENT_CONTEXT_DATA_HEADER))


def _build_wiki_content_block(
    *,
    content: str,
    client_context_data: dict[str, Any],
) -> dict[str, Any]:
    return {
        "placement": {
            "type": "message_inline",
            "slotId": DEFAULT_SLOT_ID,
        },
        "block": {
            "id": DEFAULT_SLOT_ID,
            "component": "action_card",
            "version": 1,
            "props": {
                "label": DEFAULT_ACTION_LABEL,
                "content": content,
                "format": "markdown",
                "client_context_data": client_context_data,
            },
        },
    }


async def run(task_args, context: RequestContext, http_client: HttpClient):
    del http_client

    task_args = task_args if isinstance(task_args, dict) else {}

    content = clean_text(
        _normalize_markdown_value(
            _unwrap_content_value(
                _first_value(
                    task_args,
                    "content",
                    "wiki_content",
                    "wikiContent",
                    "markdown",
                    "description",
                )
            )
        )
    )
    title = clean_text(_first_value(task_args, "title", "page_title", "pageTitle")) or "Generated Wiki Content"
    summary = clean_text(_first_value(task_args, "summary", "short_summary", "shortSummary"))
    client_context_data = _client_context_data(context)

    if not content:
        return error_result("wiki_content_required")

    payload = {
        "title": title,
        "summary": summary,
        "content": content,
    }

    return ok_result(
        {
            "content": payload,
            "ui_blocks": [
                _build_wiki_content_block(
                    content=content,
                    client_context_data=client_context_data,
                )
            ],
        }
    )
