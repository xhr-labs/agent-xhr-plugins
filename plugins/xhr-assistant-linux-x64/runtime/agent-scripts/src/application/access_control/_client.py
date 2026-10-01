"""Shared helpers for App Store access-control skills.

Contract notes verified against the dev API (2026-09-17):
- `GET /v1/ats/apps/{app_id}/settings` returns every data block with its
  supported operations, selectable relations, and currently granted relations.
- `PUT /v1/ats/apps/{app_id}/settings` is a FULL REPLACE. Blocks missing from
  the payload are silently reset to `company:admin` only, so every writer must
  send the complete block list.
- `company:admin` is re-injected by the backend on every supported operation
  and cannot be revoked.
- A relation outside the block's `options` list fails with HTTP 500, so
  relations are validated locally before the request is sent.
- Values sent for an operation whose `supported` flag is false are dropped
  without an error, so unsupported operations are rejected locally.
- `PUT /v1/as/apps/{app_id}/settings` accepts any string in `access.groups`
  without validation, so group names are validated locally.
"""

from typing import Any, Dict, List, Optional, Tuple

ADMIN_RELATION = "company:admin"
ACCESS_GROUPS = ("ADMIN", "HR_MANAGER", "EMPLOYEE")
UNRESTRICTED_ACCESS_GROUP_ALIASES = ("ALL_EMPLOYEES", "UNRESTRICTED")
OPERATIONS = ("read", "write")


def _norm(value: Any) -> str:
    return str(value or "").strip().lower()


async def list_installed_apps(context, http_client) -> Tuple[int, List[Dict[str, Any]]]:
    url = f"{context.api_base_url}/v1/as/apps/installed/menu"
    async with http_client.session() as client:
        response = await client.get(url, headers=context.headers)
        try:
            payload = response.json()
        except Exception:
            payload = {}
    data = payload.get("data") if isinstance(payload, dict) else None
    apps = []
    for item in data or []:
        if not isinstance(item, dict):
            continue
        apps.append(
            {
                "app_id": item.get("id"),
                "app_name": item.get("name"),
                "app_slug": item.get("app_slug"),
                "installed_version": item.get("version"),
            }
        )
    return response.status_code, apps


def resolve_app(apps: List[Dict[str, Any]], wanted: Optional[str]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Resolve a user-supplied app reference to exactly one installed app."""
    if not wanted:
        return None, "app is required. Available apps: " + ", ".join(
            str(a.get("app_name")) for a in apps
        )

    needle = _norm(wanted)
    exact = [
        a
        for a in apps
        if needle in (_norm(a.get("app_id")), _norm(a.get("app_slug")), _norm(a.get("app_name")))
    ]
    if len(exact) == 1:
        return exact[0], None

    partial = [a for a in apps if needle and needle in _norm(a.get("app_name"))]
    if len(partial) == 1:
        return partial[0], None
    if len(partial) > 1:
        names = ", ".join(str(a.get("app_name")) for a in partial)
        return None, f"App reference '{wanted}' matches several installed apps: {names}"

    names = ", ".join(str(a.get("app_name")) for a in apps)
    return None, f"App '{wanted}' is not installed. Installed apps: {names}"


async def get_permission_settings(context, http_client, app_id: str):
    url = f"{context.api_base_url}/v1/ats/apps/{app_id}/settings"
    async with http_client.session() as client:
        response = await client.get(url, headers=context.headers)
        try:
            payload = response.json()
        except Exception:
            payload = {}
    return response.status_code, payload


async def put_permission_settings(context, http_client, app_id: str, datablocks: List[Dict[str, Any]]):
    url = f"{context.api_base_url}/v1/ats/apps/{app_id}/settings"
    async with http_client.session() as client:
        response = await client.put(url, headers=context.headers, json={"datablocks": datablocks})
        try:
            payload = response.json()
        except Exception:
            payload = {}
    return response.status_code, payload


async def get_access_settings(context, http_client, app_id: str):
    url = f"{context.api_base_url}/v1/as/apps/{app_id}/settings"
    async with http_client.session() as client:
        response = await client.get(url, headers=context.headers)
        try:
            payload = response.json()
        except Exception:
            payload = {}
    return response.status_code, payload


async def put_access_settings(context, http_client, app_id: str, groups: List[str]):
    url = f"{context.api_base_url}/v1/as/apps/{app_id}/settings"
    async with http_client.session() as client:
        response = await client.put(url, headers=context.headers, json={"access": {"groups": groups}})
        try:
            payload = response.json()
        except Exception:
            payload = {}
    return response.status_code, payload


def parse_blocks(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Flatten the settings payload into a stable block view."""
    data = payload.get("data") if isinstance(payload, dict) else None
    raw_blocks = (data or {}).get("data_blocks") or []
    blocks = []
    for block in raw_blocks:
        if not isinstance(block, dict):
            continue
        label = block.get("label") or {}
        entry = {
            "block": block.get("name"),
            "label": label.get("default_text") if isinstance(label, dict) else None,
            "scope": block.get("category"),
            "selectable_relations": list(block.get("options") or []),
        }
        for operation in OPERATIONS:
            op = block.get(operation) or {}
            entry[operation] = {
                "supported": bool(op.get("supported")),
                "relations": list(op.get("values") or []),
            }
        blocks.append(entry)
    return blocks


def settings_version(payload: Dict[str, Any]) -> Optional[str]:
    data = payload.get("data") if isinstance(payload, dict) else None
    return (data or {}).get("version")


def to_payload_blocks(blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build the full-replace payload from a parsed block view."""
    payload = []
    for block in blocks:
        entry = {"name": block["block"]}
        for operation in OPERATIONS:
            if block[operation]["supported"]:
                entry[operation] = list(block[operation]["relations"])
        payload.append(entry)
    return payload


def describe_error(status_code: int, payload: Any) -> str:
    meta = payload.get("meta") if isinstance(payload, dict) else None
    error_code = (meta or {}).get("error_code")
    error_type = (meta or {}).get("error_type")
    detail = " ".join(part for part in (error_code, error_type) if part)
    return f"HTTP {status_code}{(' ' + detail) if detail else ''}"
