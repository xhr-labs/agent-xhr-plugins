from __future__ import annotations

from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.core.models.types import Header
from src.shared.auth import is_admin_group
from src.shared.http import format_error, request_json
from src.shared.normalize import clean_text, normalize_list, to_bool
from src.shared.result import error_result, ok_result


CUSTOM_FIELDS_ENDPOINT = "/v1/em/custom-fields"
PAGE_SIZE = 500


def _field_specs(source_choices: list[str]) -> list[dict[str, Any]]:
    source_type = "SELECT" if source_choices else "TEXT"
    source_config = {"choices": source_choices} if source_choices else None
    return [
        {
            "key": "employee_fte",
            "fieldCode": "FTE",
            "label": "FTE",
            "source": "EMPLOYEE",
            "section": "JOB_DETAILS",
            "type": "TEXT",
            "required": False,
            "config": None,
        },
        {
            "key": "calculate_capacity",
            "fieldCode": "CAP",
            "label": "CAP",
            "source": "EMPLOYEE",
            "section": "JOB_DETAILS",
            "type": "BOOLEAN",
            "required": False,
            "config": None,
        },
        {
            "key": "production_employee",
            "fieldCode": "PROD",
            "label": "PROD",
            "source": "EMPLOYEE",
            "section": "JOB_DETAILS",
            "type": "BOOLEAN",
            "required": False,
            "config": None,
        },
        {
            "key": "employee_type_fte",
            "fieldCode": "FTE",
            "label": "FTE",
            "source": "EMPLOYEE_TYPE",
            "section": "EMPLOYEE_TYPE",
            "type": "TEXT",
            "required": False,
            "config": None,
        },
        {
            "key": "department_source",
            "fieldCode": "SOURCE",
            "label": "SOURCE",
            "source": "DEPARTMENT",
            "section": "DEPARTMENT",
            "type": source_type,
            "required": False,
            "config": source_config,
        },
    ]


def _request_header(request_headers: Any, name: Header) -> str | None:
    if not isinstance(request_headers, dict):
        return None
    normalized_headers = {
        str(key).lower(): value
        for key, value in request_headers.items()
        if key is not None
    }
    return clean_text(normalized_headers.get(name.value))


def _field_identity(field: dict[str, Any]) -> tuple[str, str, str] | None:
    field_code = field.get("fieldCode")
    source = field.get("source")
    section = field.get("section")
    if not all(isinstance(value, str) and value.strip() for value in (field_code, source, section)):
        return None
    return field_code.strip().upper(), source.strip().upper(), section.strip().upper()


def _extract_fields(payload: Any) -> list[dict[str, Any]] | None:
    if not isinstance(payload, dict):
        return None
    data = payload.get("data")
    return data if isinstance(data, list) else None


async def _fetch_all_fields(client: Any, endpoint: str, headers: dict[str, str]) -> tuple[list[dict[str, Any]] | None, dict[str, Any] | None]:
    fields: list[dict[str, Any]] = []
    page = 0
    total_pages = 1

    while page < total_pages:
        status_code, payload = await request_json(
            client,
            "GET",
            endpoint,
            params={"page": page, "size": PAGE_SIZE},
            headers=headers,
        )
        if status_code < 200 or status_code >= 300:
            return None, {
                "status": status_code,
                "error": format_error(payload),
            }

        page_fields = _extract_fields(payload)
        if page_fields is None:
            return None, {
                "status": status_code,
                "error": {"message": "Custom field list response did not contain a data list."},
            }
        fields.extend(field for field in page_fields if isinstance(field, dict))

        meta = payload.get("meta")
        if isinstance(meta, dict):
            raw_total_pages = meta.get("totalPages")
            if isinstance(raw_total_pages, int) and raw_total_pages > 0:
                total_pages = raw_total_pages
        page += 1

    return fields, None


def _preview(specs: list[dict[str, Any]], fields: list[dict[str, Any]]) -> dict[str, Any]:
    existing_by_identity: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for field in fields:
        identity = _field_identity(field)
        if identity:
            existing_by_identity.setdefault(identity, []).append(field)

    existing = []
    conflicts = []
    inactive = []
    missing = []
    for spec in specs:
        identity = (spec["fieldCode"], spec["source"], spec["section"])
        matches = existing_by_identity.get(identity, [])
        if not matches:
            missing.append(spec)
            continue

        field = matches[0]
        if bool(field.get("deleted", False)):
            status = "INACTIVE"
        elif str(field.get("type", "")).upper() in _acceptable_types(spec):
            status = "EXISTS"
        else:
            status = "CONFLICT"
        item = {
            "key": spec["key"],
            "fieldCode": spec["fieldCode"],
            "source": spec["source"],
            "section": spec["section"],
            "expectedType": spec["type"],
            "existingType": field.get("type"),
            "existingId": field.get("id"),
            "deleted": bool(field.get("deleted", False)),
            "status": status,
        }
        if status == "EXISTS":
            existing.append(item)
        elif status == "INACTIVE":
            inactive.append(item)
        else:
            conflicts.append(item)

    return {
        "existing": existing,
        "conflicts": conflicts,
        "inactive": inactive,
        "missing": missing,
    }


def _acceptable_types(spec: dict[str, Any]) -> set[str]:
    if spec["key"] == "department_source" and spec["type"] == "TEXT":
        return {"TEXT", "SELECT"}
    return {spec["type"]}


def _create_payload(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": spec["label"],
        "label": spec["label"],
        "field_code": spec["fieldCode"],
        "placeholder": "",
        "source": spec["source"],
        "section": spec["section"],
        "type": spec["type"],
        "config": spec["config"],
        "required": spec["required"],
        "deleted": False,
        "applicability_scope": "ALL",
        "targets": [],
    }


async def run(task_args, context: RequestContext, http_client: HttpClient):
    request_headers = context.request_headers if isinstance(context.request_headers, dict) else {}
    if not is_admin_group(request_headers.get("xhr-groups")):
        return error_result("You must have Admin permission to create Allocation custom fields.")

    company_id = _request_header(request_headers, Header.X_COMPANY_ID)
    if not company_id:
        return error_result("Missing required request header: xhr-company-id")

    employee_id = _request_header(request_headers, Header.X_EMPLOYEE_ID)
    headers = dict(context.headers)
    headers["Xhr-Company-Id"] = company_id
    if employee_id:
        headers["Xhr-Employee-Id"] = employee_id

    task_args = task_args if isinstance(task_args, dict) else {}
    source_choices = normalize_list(
        task_args.get("source_choices")
        or task_args.get("sourceChoices")
        or task_args.get("source_choice")
        or task_args.get("sourceChoice")
    )
    confirmed = to_bool(task_args.get("confirm"))
    endpoint = f"{context.api_base_url}{CUSTOM_FIELDS_ENDPOINT}"

    async with http_client.session() as client:
        fields, fetch_error = await _fetch_all_fields(client, endpoint, headers)
        if fetch_error:
            return error_result(
                f"Unable to inspect existing custom fields: {fetch_error}"
            )

        specs = _field_specs(source_choices)
        preview = _preview(specs, fields or [])
        if not confirmed:
            return ok_result({
                "status": "PREVIEW",
                "confirmationRequired": True,
                "sourceFieldType": specs[-1]["type"],
                "sourceChoices": source_choices,
                "fields": specs,
                **preview,
                "nextAction": "Ask the Admin to confirm creation of missing fields.",
            })

        created = []
        failed = []
        for spec in preview["missing"]:
            payload = _create_payload(spec)
            try:
                status_code, response_payload = await request_json(
                    client,
                    "POST",
                    endpoint,
                    json_data=payload,
                    headers=headers,
                )
            except Exception as exc:
                failed.append({
                    "key": spec["key"],
                    "fieldCode": spec["fieldCode"],
                    "source": spec["source"],
                    "section": spec["section"],
                    "error": format_error(exc=exc),
                })
                continue

            if status_code < 200 or status_code >= 300:
                failed.append({
                    "key": spec["key"],
                    "fieldCode": spec["fieldCode"],
                    "source": spec["source"],
                    "section": spec["section"],
                    "status": status_code,
                    "error": format_error(response_payload),
                })
                continue

            created.append({
                "key": spec["key"],
                "fieldCode": spec["fieldCode"],
                "source": spec["source"],
                "section": spec["section"],
                "type": spec["type"],
                "response": response_payload.get("data") if isinstance(response_payload, dict) else response_payload,
            })

    return ok_result({
        "status": "COMPLETED"
        if not failed and not preview["conflicts"] and not preview["inactive"]
        else "PARTIAL",
        "created": created,
        "skipped": preview["existing"],
        "conflicts": preview["conflicts"],
        "inactive": preview["inactive"],
        "failed": failed,
        "sourceFieldType": specs[-1]["type"],
        "sourceChoices": source_choices,
    })
