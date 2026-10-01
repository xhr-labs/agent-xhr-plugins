"""Cancel (withdraw) one of the caller's pending expense requests."""

from __future__ import annotations

from src.application.exm.common import (
    as_args,
    base_url,
    call_json,
    entity_result,
    require_uuid,
    value,
    write_headers,
)
from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text


async def run(task_args, context: RequestContext, http_client: HttpClient):
    args = as_args(task_args)

    expense_id, error = require_uuid(
        value(args, "expense_id", "expenseId", "id"),
        "expense_id",
        lookup_hint="skills/exm/list_my_expenses",
    )
    if error:
        return error

    reason = clean_text(value(args, "reason", "comments"))
    body = {"reason": reason} if reason else None

    payload, failure = await call_json(
        http_client,
        "PATCH",
        f"{base_url(context)}/expenses/{expense_id}/cancel",
        headers=write_headers(context, args),
        body=body,
        feature="cancel this expense",
    )
    if failure:
        return failure

    return entity_result(payload, cancelled=True)
