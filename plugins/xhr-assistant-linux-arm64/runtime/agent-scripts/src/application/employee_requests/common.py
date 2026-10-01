from __future__ import annotations

import re
import uuid
from typing import Any

from src.core.models.request_context import RequestContext
from src.shared.http import format_error, request_json
from src.shared.normalize import clean_text
from src.shared.result import error_result, ok_result


_UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
_TICKET_RE = re.compile(r"^ER-\d{4}-\d{6}$", re.IGNORECASE)


def value(args: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        candidate = args.get(key)
        if candidate is not None:
            return candidate
    return None


def idempotency_key(args: dict[str, Any]) -> str:
    return clean_text(value(args, "idempotency_key", "idempotencyKey")) or str(uuid.uuid4())


def normalize_if_match(raw: Any) -> str | None:
    """Return the backend `If-Match` value (`"<n>"`) or None when no usable version was given.

    Accepts `3`, `"3"`, `'"3"'` or `W/"3"`; anything that is not a non-negative integer is rejected.
    """
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, int):
        return f'"{raw}"' if raw >= 0 else None
    text = clean_text(raw)
    if not text:
        return None
    text = text.strip()
    if text.upper().startswith("W/"):
        text = text[2:].strip()
    text = text.strip("'\"").strip()
    if not text.isdigit():
        return None
    return f'"{int(text)}"'


def version_error(action: str | None = None) -> dict[str, Any]:
    what = f" for `{action}`" if action else ""
    return error_result(
        "version_required: the backend requires If-Match with the current numeric `version`"
        f"{what}. Read the request/request-type detail first and pass --if-match <version> "
        "(the `version` field of the latest read, or the `version` returned by the previous write)."
    )


def write_headers(
    context: RequestContext,
    args: dict[str, Any],
) -> dict[str, str]:
    headers = dict(context.headers)
    headers["Idempotency-Key"] = idempotency_key(args)
    if_match = normalize_if_match(value(args, "if_match", "ifMatch", "version", "expected_version"))
    if if_match:
        headers["If-Match"] = if_match
    return headers


def has_version(args: dict[str, Any]) -> bool:
    return normalize_if_match(value(args, "if_match", "ifMatch", "version", "expected_version")) is not None


def require_uuid(raw: Any, name: str, *, lookup_hint: str) -> tuple[str | None, dict[str, Any] | None]:
    """Validate that `raw` is a UUID. Returns (uuid, None) or (None, error_result)."""
    text = clean_text(raw)
    if not text:
        return None, error_result(f"{name}_required")
    if _UUID_RE.match(text):
        return text.lower(), None
    if _TICKET_RE.match(text):
        return None, error_result(
            f"{name}_must_be_uuid: '{text}' is a human ticket number, not an ID. "
            f"Resolve the UUID first via {lookup_hint}, then pass it as --{name.replace('_', '-')}."
        )
    return None, error_result(
        f"{name}_must_be_uuid: '{text}' is not a UUID. Never guess IDs; resolve it via {lookup_hint}."
    )


def require_enum(raw: Any, name: str, allowed: tuple[str, ...], *, case_insensitive: bool = True) -> tuple[str | None, dict[str, Any] | None]:
    text = clean_text(raw)
    if not text:
        return None, None
    for option in allowed:
        if text == option or (case_insensitive and text.lower() == option.lower()):
            return option, None
    return None, error_result(f"{name}_invalid: '{text}'. Allowed values: {', '.join(allowed)}.")


def require_body_keys(body: dict[str, Any] | None, action: str, required: tuple[str, ...], optional: tuple[str, ...] = ()) -> dict[str, Any] | None:
    body = body or {}
    missing = [key for key in required if clean_text(body.get(key)) is None and body.get(key) not in (True, False) and not isinstance(body.get(key), (int, float, list, dict))]
    unknown = [key for key in body if key not in required and key not in optional]
    if missing or unknown:
        parts = []
        if missing:
            parts.append(f"missing {', '.join(missing)}")
        if unknown:
            parts.append(f"unknown {', '.join(unknown)}")
        return error_result(
            f"body_invalid for `{action}`: {'; '.join(parts)}. Expected body keys: "
            f"required [{', '.join(required)}]" + (f", optional [{', '.join(optional)}]" if optional else "") + "."
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
) -> tuple[Any | None, dict[str, Any] | None]:
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
        except Exception as exc:
            return None, error_result(str(format_error(exc=exc)))

    if status_code < 200 or status_code >= 300:
        return None, error_result(str(format_error(payload)))
    return payload, None


def unwrap_data(payload: Any) -> Any:
    return payload.get("data") if isinstance(payload, dict) else None


def page_result(payload: Any, key: str) -> dict[str, Any]:
    data = unwrap_data(payload)
    if not isinstance(data, list):
        data = []
    meta = payload.get("meta") if isinstance(payload, dict) else None
    return {
        key: data,
        "count": len(data),
        "meta": meta if isinstance(meta, dict) else {},
    }


def success(payload: Any, **extra: Any) -> dict[str, Any]:
    return ok_result({"data": unwrap_data(payload), **extra})
