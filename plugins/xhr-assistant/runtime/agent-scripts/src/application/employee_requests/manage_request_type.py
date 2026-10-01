import json

from src.application.employee_requests.common import (
    call_json,
    has_version,
    require_uuid,
    success,
    value,
    write_headers,
)
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text
from src.shared.result import error_result


ACTIONS = ("create", "create_version", "get_version", "list_versions", "update_draft", "publish", "retire", "restore")
VERSIONED_ACTIONS = {"update_draft", "publish", "retire", "restore"}
DRAFT_KEYS = (
    "name", "description", "instructions", "source_locale", "form_schema", "default_queue_id", "default_priority",
    "first_response_target_seconds", "resolution_target_seconds", "attachment_policy", "sensitivity_key",
    "processing_purpose", "lawful_basis_key", "special_category_condition_key", "retention_policy_key",
    "business_owner_employee_id",
)


def _draft_error(action: str) -> dict:
    return error_result(
        f"draft_required for `{action}`: pass --body-json '{{\"request_type_key\": \"UPPER_SNAKE\", \"draft\": {{...}}}}' "
        f"(for create) or '{{\"draft\": {{...}}}}' (for update_draft). Draft keys: {', '.join(DRAFT_KEYS)}. "
        "Copy the shape from `get_version` of an existing type; `form_schema` is {\"fields\": [{key,type,label,required,options?}]}."
    )


async def run(task_args, context: RequestContext, http_client):
    args = task_args if isinstance(task_args, dict) else {}
    action = clean_text(value(args, "action", "operation"))
    if action not in ACTIONS:
        return error_result(f"unsupported_action: {', '.join(ACTIONS)}")

    request_type_id = None
    if action != "create":
        request_type_id, failure = require_uuid(
            value(args, "request_type_id", "requestTypeId", "id"), "request_type_id",
            lookup_hint="`list_request_types` (field `id`)",
        )
        if failure:
            return failure
    version_id = None
    if action in {"get_version", "update_draft", "publish"}:
        version_id, failure = require_uuid(
            value(args, "version_id", "versionId"), "version_id",
            lookup_hint="`manage_request_type --action list_versions` (field `id` of the version)",
        )
        if failure:
            return failure

    body = value(args, "body", "payload", "body_json", "draft_json")
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            return error_result("body_json_invalid")
    if body is not None and not isinstance(body, dict):
        return error_result("body_json_must_be_object")

    if action == "create":
        path, method = "request-types", "POST"
        if body is None:
            draft = value(args, "draft")
            key = clean_text(value(args, "request_type_key", "requestTypeKey"))
            body = {"request_type_key": key, "draft": draft} if key and isinstance(draft, dict) else None
        if not isinstance(body, dict) or not isinstance(body.get("draft"), dict) or not clean_text(body.get("request_type_key")):
            return _draft_error(action)
    elif action == "create_version":
        path, method, body = f"request-types/{request_type_id}/versions", "POST", None
    elif action == "list_versions":
        path, method, body = f"request-types/{request_type_id}/versions", "GET", None
    elif action == "get_version":
        path, method, body = f"request-types/{request_type_id}/versions/{version_id}", "GET", None
    elif action == "update_draft":
        path, method = f"request-types/{request_type_id}/versions/{version_id}", "PATCH"
        if body is None:
            draft = value(args, "draft")
            body = {"draft": draft} if isinstance(draft, dict) else None
        if not isinstance(body, dict) or not isinstance(body.get("draft"), dict):
            return _draft_error(action)
    elif action == "publish":
        path, method = f"request-types/{request_type_id}/versions/{version_id}/activation", "POST"
        expected = value(args, "expected_draft_version", "expectedDraftVersion")
        if expected is None and isinstance(body, dict):
            expected = body.get("expected_draft_version", body.get("expectedDraftVersion"))
        if expected is None:
            # Mirror the app: expectedDraftVersion is the draft's current `version`, read it instead of guessing.
            detail, failure = await call_json(
                http_client, "GET",
                f"{context.api_base_url}/v1/erequest/backoffice/request-types/{request_type_id}/versions/{version_id}",
                headers=context.headers,
            )
            if failure:
                return failure
            draft = detail.get("data") if isinstance(detail, dict) else None
            if not isinstance(draft, dict) or draft.get("state") != "DRAFT":
                return error_result("version_not_draft: only a version in state DRAFT can be published")
            expected = draft.get("version")
        try:
            expected = int(expected)
        except (TypeError, ValueError):
            return error_result(
                "expected_draft_version_invalid: it must be the DRAFT version's numeric `version` field "
                "(not `version_number`); omit the flag to let the script read it."
            )
        body = {"expected_draft_version": expected}
    elif action == "retire":
        path, method, body = f"request-types/{request_type_id}/retirement", "POST", None
    else:
        path, method, body = f"request-types/{request_type_id}/restoration", "POST", None

    if action in VERSIONED_ACTIONS and not has_version(args):
        return error_result(
            f"version_required for `{action}`: pass --if-match <version>. For publish/retire/restore use the ROOT "
            "request type `version` (from list_request_types); for update_draft use the DRAFT version's `version` "
            "(from get_version)."
        )

    headers = context.headers if method == "GET" else write_headers(context, args)
    params = None
    if method == "GET":
        params = {"pageSize": max(1, min(int(value(args, "page_size", "pageSize") or 25), 100))}
        cursor = clean_text(value(args, "cursor"))
        if cursor:
            params["cursor"] = cursor
    payload, failure = await call_json(
        http_client, method, f"{context.api_base_url}/v1/erequest/backoffice/{path}",
        headers=headers, params=params, body=body,
    )
    if failure:
        return failure
    return success(payload, action=action, request_type_id=request_type_id, version_id=version_id)
