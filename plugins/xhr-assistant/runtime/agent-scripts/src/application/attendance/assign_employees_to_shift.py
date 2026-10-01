import json

from src.application.attendance.get_shift import run as get_shift_run
from src.application.employee.search_employees import run as search_employees_run
from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text, normalize_list
from src.shared.result import error_result, ok_result


ERROR_SHIFT_REQUIRED = "shift_id_or_shift_name_required"
ERROR_EMPLOYEE_REQUIRED = "employee_ids_or_employee_names_required"


def _normalize_text_list(value):
    values = normalize_list(value)
    normalized = []
    for item in values:
        text = clean_text(item)
        if text:
            normalized.append(text)
    return normalized


def _dedupe_keep_order(values):
    deduped = []
    seen = set()
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped


def _normalize_employee(item):
    if not isinstance(item, dict):
        return None
    employee_id = item.get("id") or item.get("employee_id")
    if not employee_id:
        return None
    return {
        "employee_id": employee_id,
        "name": item.get("name") or item.get("full_name") or item.get("display_name"),
        "code": item.get("code") or item.get("employee_code"),
        "email": item.get("email"),
        "raw": item,
    }


async def _resolve_shift(task_args, context: RequestContext, http_client: HttpClient):
    shift_id = clean_text(task_args.get("shift_id"))
    shift_name = clean_text(task_args.get("shift_name"))

    if shift_id:
        return {
            "ok": True,
            "shift_id": shift_id,
            "shift_name": shift_name,
            "resolution": "provided_shift_id",
            "shift": None,
            "candidates": [],
        }

    if not shift_name:
        return error_result(ERROR_SHIFT_REQUIRED)

    shift_result = await get_shift_run(
        {
            "shift_name": shift_name,
            "search_keyword": shift_name,
            "page": 0,
            "size": 20,
        },
        context,
        http_client,
    )
    if not shift_result.get("ok"):
        return shift_result

    data = shift_result.get("data") or {}
    exact_matches = data.get("exact_matches") or []

    if len(exact_matches) == 0:
        return error_result(f"shift_not_found_exact_name:{shift_name}")
    if len(exact_matches) > 1:
        candidate_ids = [item.get("shift_id") for item in exact_matches if item.get("shift_id")]
        return error_result(
            f"shift_name_ambiguous:{shift_name}:{json.dumps(candidate_ids, ensure_ascii=False)}"
        )

    shift = exact_matches[0]
    return {
        "ok": True,
        "shift_id": shift.get("shift_id"),
        "shift_name": shift.get("name"),
        "resolution": "resolved_from_shift_name",
        "shift": shift,
        "candidates": exact_matches,
    }


async def _resolve_employee_name(name, context: RequestContext, http_client: HttpClient):
    result = await search_employees_run({"name": name}, context, http_client)
    if not result.get("ok"):
        return result

    payload = result.get("data") or {}
    items = payload.get("data") or []
    normalized = []
    lowered_target = name.strip().lower()

    for item in items:
        formatted = _normalize_employee(item)
        if not formatted:
            continue
        employee_name = clean_text(formatted.get("name"))
        if employee_name and employee_name.strip().lower() == lowered_target:
            normalized.append(formatted)

    if len(normalized) == 0:
        return error_result(f"employee_name_not_found_exact:{name}")
    if len(normalized) > 1:
        candidate_ids = [item.get("employee_id") for item in normalized if item.get("employee_id")]
        return error_result(
            f"employee_name_ambiguous:{name}:{json.dumps(candidate_ids, ensure_ascii=False)}"
        )

    employee = normalized[0]
    return {
        "ok": True,
        "employee": employee,
        "resolution": "resolved_from_employee_name",
    }


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers
    args = task_args if isinstance(task_args, dict) else {}

    provided_employee_ids = _normalize_text_list(args.get("employee_ids") or args.get("employee_id"))
    employee_names = _normalize_text_list(args.get("employee_names") or args.get("employee_name"))

    if not clean_text(args.get("shift_id")) and not clean_text(args.get("shift_name")):
        return error_result(ERROR_SHIFT_REQUIRED)
    if not provided_employee_ids and not employee_names:
        return error_result(ERROR_EMPLOYEE_REQUIRED)

    shift_resolution = await _resolve_shift(args, context, http_client)
    if not shift_resolution.get("ok"):
        return shift_resolution

    resolved_employee_ids = list(provided_employee_ids)
    resolved_employees = []
    resolution_errors = []

    for employee_name in employee_names:
        resolved = await _resolve_employee_name(employee_name, context, http_client)
        if not resolved.get("ok"):
            resolution_errors.append({
                "employee_name": employee_name,
                "error": resolved.get("error"),
            })
            continue

        employee = resolved.get("employee") or {}
        employee_id = employee.get("employee_id")
        if employee_id:
            resolved_employee_ids.append(employee_id)
        resolved_employees.append(employee)

    if resolution_errors:
        return ok_result({
            "assigned": False,
            "failure_stage": "resolve_employees",
            "shift_id": shift_resolution.get("shift_id"),
            "shift_name": shift_resolution.get("shift_name"),
            "employee_ids": _dedupe_keep_order(resolved_employee_ids),
            "resolved_employee_names": [item.get("name") for item in resolved_employees if item.get("name")],
            "errors": resolution_errors,
            "nextAction": "fix_employee_resolution_errors",
        })

    final_employee_ids = _dedupe_keep_order(resolved_employee_ids)
    if not final_employee_ids:
        return error_result(ERROR_EMPLOYEE_REQUIRED)

    url = f"{api_base_url}/v1/atd/shifts/{shift_resolution.get('shift_id')}/employees"
    payload = {
        "employee_ids": final_employee_ids,
    }

    async with http_client.session() as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            status_code = response.status_code
            try:
                response_payload = response.json()
            except Exception:
                response_payload = {}
        except Exception as exc:
            return error_result(str(exc))

    if status_code < 200 or status_code >= 300:
        return error_result(
            f"assign_employees_to_shift_failed:{status_code}:{json.dumps(response_payload, ensure_ascii=False)}"
        )

    return ok_result({
        "assigned": True,
        "shift_id": shift_resolution.get("shift_id"),
        "shift_name": shift_resolution.get("shift_name"),
        "shift_resolution": shift_resolution.get("resolution"),
        "employee_ids": final_employee_ids,
        "provided_employee_ids": provided_employee_ids,
        "resolved_employee_names": [item.get("name") for item in resolved_employees if item.get("name")],
        "resolved_employees": resolved_employees,
        "payload": payload,
        "response": response_payload,
        "nextAction": "review_assignment_status",
    })
