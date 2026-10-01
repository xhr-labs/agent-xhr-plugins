"""Create, update, or delete one expense category (Configuration -> Categories)."""

from __future__ import annotations

import re
from typing import Any

from src.application.exm.common import (
    as_args,
    base_url,
    call_json,
    entity_result,
    require_enum,
    require_uuid,
    value,
    write_headers,
)
from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text
from src.shared.result import error_result, ok_result


ACTIONS = ("create", "update", "delete")
CODE_RE = re.compile(r"^[A-Za-z0-9_-]+$")
MAX_DESCRIPTION = 500


def _form(args: dict[str, Any], *, require_name: bool) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    body: dict[str, Any] = {}

    name = clean_text(value(args, "name"))
    if name:
        body["name"] = name
    elif require_name:
        return None, error_result("name_required: a category needs a name, for example 'Travel'.")

    code = clean_text(value(args, "code"))
    if code:
        if not CODE_RE.match(code):
            return None, error_result(
                "code_invalid: the code may contain only letters, numbers, hyphens, and underscores."
            )
        body["code"] = code

    description = clean_text(value(args, "description"))
    if description:
        if len(description) > MAX_DESCRIPTION:
            return None, error_result(
                f"description_too_long: keep the description to {MAX_DESCRIPTION} characters or fewer."
            )
        body["description"] = description

    if not body:
        return None, error_result(
            "no_changes: pass at least one of --name, --code, or --description."
        )
    return body, None


async def run(task_args, context: RequestContext, http_client: HttpClient):
    args = as_args(task_args)

    action, error = require_enum(value(args, "action"), "action", ACTIONS)
    if error:
        return error
    if not action:
        return error_result(f"action_required: pass --action with one of {', '.join(ACTIONS)}.")

    root = f"{base_url(context)}/categories"
    headers = write_headers(context, args)

    if action == "create":
        body, error = _form(args, require_name=True)
        if error:
            return error
        payload, failure = await call_json(
            http_client,
            "POST",
            root,
            headers=headers,
            body=body,
            feature="create expense categories",
        )
        if failure:
            return failure
        return entity_result(payload, action=action)

    category_id, error = require_uuid(
        value(args, "category_id", "categoryId", "id"),
        "category_id",
        lookup_hint="skills/exm/list_expense_categories",
    )
    if error:
        return error

    if action == "update":
        body, error = _form(args, require_name=False)
        if error:
            return error
        payload, failure = await call_json(
            http_client,
            "PATCH",
            f"{root}/{category_id}",
            headers=headers,
            body=body,
            feature="update expense categories",
        )
        if failure:
            return failure
        return entity_result(payload, action=action, category_id=category_id)

    payload, failure = await call_json(
        http_client,
        "DELETE",
        f"{root}/{category_id}",
        headers=headers,
        feature="delete expense categories",
    )
    if failure:
        return failure
    return ok_result({"action": action, "category_id": category_id, "deleted": True})
