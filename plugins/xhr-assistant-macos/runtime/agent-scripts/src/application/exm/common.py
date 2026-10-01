"""Shared helpers for Expense Management (EXM) skills.

Every leaf under ``skills/exm`` talks to the Expense Management micro-app backend at
``{api_base_url}/v1/exm``, the same contract the ``expenses`` micro-app consumes. The
helpers here keep identifier validation, enum checking, and envelope unwrapping in one
place so the individual tools stay thin.
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import date
from typing import Any

from src.core.models.request_context import RequestContext
from src.shared.http import format_error, request_json
from src.shared.normalize import clean_int, clean_text
from src.shared.result import error_result, ok_result


API_PREFIX = "/v1/exm"
CM_API_PREFIX = "/v1/cm"

EXPENSE_STATUSES = (
    "PENDING_APPROVAL",
    "APPROVED",
    "REJECTED",
    "CANCELLED",
    "REIMBURSED",
)
POLICY_STATUSES = ("DRAFT", "SCHEDULED", "ACTIVE", "ARCHIVED")

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

_UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


def base_url(context: RequestContext) -> str:
    return f"{context.api_base_url}{API_PREFIX}"


def value(args: dict[str, Any], *keys: str) -> Any:
    """First non-null value among ``keys``; tolerates snake_case and camelCase injection."""
    for key in keys:
        candidate = args.get(key)
        if candidate is not None:
            return candidate
    return None


def as_args(task_args: Any) -> dict[str, Any]:
    return task_args if isinstance(task_args, dict) else {}


def idempotency_key(args: dict[str, Any]) -> str:
    return clean_text(value(args, "idempotency_key", "idempotencyKey")) or str(uuid.uuid4())


def write_headers(context: RequestContext, args: dict[str, Any]) -> dict[str, str]:
    headers = dict(context.headers)
    headers["Idempotency-Key"] = idempotency_key(args)
    return headers


def require_uuid(raw: Any, name: str, *, lookup_hint: str) -> tuple[str | None, dict[str, Any] | None]:
    """Validate ``raw`` is a UUID. Returns ``(uuid, None)`` or ``(None, error_result)``."""
    text = clean_text(raw)
    if not text:
        return None, error_result(
            f"{name}_required: pass --{name.replace('_', '-')} <uuid>. Resolve it via {lookup_hint}."
        )
    if _UUID_RE.match(text):
        return text.lower(), None
    return None, error_result(
        f"{name}_must_be_uuid: '{text}' is not a UUID. Never guess IDs; resolve it via {lookup_hint}."
    )


def optional_uuid(raw: Any, name: str, *, lookup_hint: str) -> tuple[str | None, dict[str, Any] | None]:
    if clean_text(raw) is None:
        return None, None
    return require_uuid(raw, name, lookup_hint=lookup_hint)


def require_enum(raw: Any, name: str, allowed: tuple[str, ...]) -> tuple[str | None, dict[str, Any] | None]:
    text = clean_text(raw)
    if not text:
        return None, None
    for option in allowed:
        if text.upper() == option.upper():
            return option, None
    return None, error_result(f"{name}_invalid: '{text}'. Allowed values: {', '.join(allowed)}.")


def normalize_statuses(raw: Any) -> tuple[list[str], dict[str, Any] | None]:
    """Accept a repeated flag, a comma-separated string, or a list of expense statuses."""
    if raw is None:
        return [], None
    candidates: list[str] = []
    items = raw if isinstance(raw, list) else [raw]
    for item in items:
        text = clean_text(item)
        if not text:
            continue
        candidates.extend(part.strip() for part in text.split(",") if part.strip())

    statuses: list[str] = []
    for candidate in candidates:
        matched = next(
            (option for option in EXPENSE_STATUSES if option.upper() == candidate.upper()),
            None,
        )
        if matched is None:
            return [], error_result(
                f"status_invalid: '{candidate}'. Allowed values: {', '.join(EXPENSE_STATUSES)}."
            )
        if matched not in statuses:
            statuses.append(matched)
    return statuses, None


def iso_date(raw: Any, name: str) -> tuple[str | None, dict[str, Any] | None]:
    text = clean_text(raw)
    if not text:
        return None, None
    try:
        return date.fromisoformat(text).isoformat(), None
    except ValueError:
        return None, error_result(f"{name}_invalid: expected YYYY-MM-DD, got '{text}'.")


def date_range(args: dict[str, Any]) -> tuple[str | None, str | None, dict[str, Any] | None]:
    date_from, error = iso_date(value(args, "date_from", "dateFrom"), "date_from")
    if error:
        return None, None, error
    date_to, error = iso_date(value(args, "date_to", "dateTo"), "date_to")
    if error:
        return None, None, error
    if date_from and date_to and date_from > date_to:
        return None, None, error_result("invalid_period: date_from must be on or before date_to.")
    return date_from, date_to, None


def paging(args: dict[str, Any]) -> dict[str, Any]:
    page = clean_int(value(args, "page"))
    size = clean_int(value(args, "size", "page_size", "pageSize"))
    params: dict[str, Any] = {"size": max(1, min(size or DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE))}
    if page is not None and page >= 0:
        params["page"] = page
    return params


def parse_json_object(raw: Any, name: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Parse a ``--*-json`` flag into a dict. Returns ``(None, None)`` when absent."""
    if raw is None:
        return None, None
    if isinstance(raw, dict):
        return raw, None
    text = clean_text(raw)
    if not text:
        return None, None
    try:
        parsed = json.loads(text)
    except ValueError as exc:
        return None, error_result(f"{name}_invalid: not valid JSON ({exc}).")
    if not isinstance(parsed, dict):
        return None, error_result(f"{name}_invalid: expected a JSON object.")
    return parsed, None


def parse_json_array(raw: Any, name: str) -> tuple[list[Any] | None, dict[str, Any] | None]:
    if raw is None:
        return None, None
    if isinstance(raw, list):
        return raw, None
    text = clean_text(raw)
    if not text:
        return None, None
    try:
        parsed = json.loads(text)
    except ValueError as exc:
        return None, error_result(f"{name}_invalid: not valid JSON ({exc}).")
    if not isinstance(parsed, list):
        return None, error_result(f"{name}_invalid: expected a JSON array.")
    return parsed, None


def permission_error(status_code: int, feature: str) -> dict[str, Any] | None:
    if status_code in (401, 403):
        return error_result(
            f"permission_denied: the signed-in user is not allowed to {feature}. "
            "Ask an Expense Management admin for access; do not retry with other arguments."
        )
    return None


async def call_json(
    http_client,
    method: str,
    url: str,
    *,
    headers: dict[str, str],
    params: dict[str, Any] | None = None,
    body: Any = None,
    feature: str = "use this Expense Management feature",
) -> tuple[Any | None, dict[str, Any] | None]:
    """Perform one backend call. Returns ``(payload, None)`` or ``(None, error_result)``."""
    async with http_client.session() as client:
        try:
            status_code, payload = await request_json(
                client,
                method,
                url,
                headers=headers,
                params=params,
                json_data=body if body is not None else None,
            )
        except Exception as exc:  # network / transport failure
            return None, error_result(str(format_error(exc=exc)))

    if status_code == 404:
        return None, error_result(
            "not_found: the requested Expense Management record does not exist or is not visible to the caller."
        )
    denied = permission_error(status_code, feature)
    if denied is not None:
        return None, denied
    if status_code < 200 or status_code >= 300:
        message = format_error(payload).get("message") or "Request failed"
        return None, error_result(f"expense_request_failed: {status_code} {message}")
    return payload, None


def unwrap_data(payload: Any) -> Any:
    return payload.get("data") if isinstance(payload, dict) else payload


def unwrap_entity(payload: Any) -> Any:
    """Resolve ``{"data": {...}}`` and bare-object envelopes to the entity itself."""
    data = unwrap_data(payload)
    if isinstance(data, (dict, list)):
        return data
    return payload if isinstance(payload, (dict, list)) else None


def unwrap_list(payload: Any) -> list[Any]:
    """Resolve the list envelopes the EXM backend uses: bare list, ``data``, ``content``."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("data", "content", "items"):
            candidate = payload.get(key)
            if isinstance(candidate, list):
                return candidate
            if isinstance(candidate, dict):
                nested = candidate.get("content")
                if isinstance(nested, list):
                    return nested
    return []


def page_meta(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    meta = payload.get("meta")
    if isinstance(meta, dict):
        return meta
    data = payload.get("data")
    source = data if isinstance(data, dict) else payload
    collected: dict[str, Any] = {}
    for key in ("page", "size", "totalElements", "total_elements", "total", "hasNext"):
        if key in source:
            collected[key] = source[key]
    return collected


def list_result(payload: Any, key: str, **extra: Any) -> dict[str, Any]:
    items = unwrap_list(payload)
    return ok_result({key: items, "count": len(items), "meta": page_meta(payload), **extra})


def entity_result(payload: Any, **extra: Any) -> dict[str, Any]:
    return ok_result({"data": unwrap_entity(payload), **extra})
