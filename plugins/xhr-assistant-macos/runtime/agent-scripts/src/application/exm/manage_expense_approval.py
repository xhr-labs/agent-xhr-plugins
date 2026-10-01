"""Approve or reject one assigned expense approval task, or approve the whole queue."""

from __future__ import annotations

import uuid

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
from src.shared.result import error_result


ACTIONS = ("approve", "reject", "approve_all")


async def run(task_args, context: RequestContext, http_client: HttpClient):
    args = as_args(task_args)

    raw_action = clean_text(value(args, "action"))
    if raw_action:
        raw_action = raw_action.replace("-", "_")
    action, error = require_enum(raw_action, "action", ACTIONS)
    if error:
        return error
    if not action:
        return error_result(f"action_required: pass --action with one of {', '.join(ACTIONS)}.")

    comments = clean_text(value(args, "comments", "reason", "note"))
    headers = write_headers(context, args)

    if action == "approve_all":
        payload, failure = await call_json(
            http_client,
            "POST",
            f"{base_url(context)}/expenses/approvals/approve-all",
            headers=headers,
            body={"operation_id": str(uuid.uuid4())},
            feature="approve every pending expense in the queue",
        )
        if failure:
            return failure
        return entity_result(payload, action=action)

    expense_id, error = require_uuid(
        value(args, "expense_id", "expenseId", "id"),
        "expense_id",
        lookup_hint="skills/exm/list_expense_approvals --view pending",
    )
    if error:
        return error

    if action == "reject" and not comments:
        return error_result(
            "comments_required: a rejection needs a reason. Ask the user for it and pass --comments."
        )

    payload, failure = await call_json(
        http_client,
        "PATCH",
        f"{base_url(context)}/expenses/{expense_id}/{action}",
        headers=headers,
        body={"comments": comments} if comments else {},
        feature=f"{action} this expense",
    )
    if failure:
        return failure

    return entity_result(payload, action=action, expense_id=expense_id)
