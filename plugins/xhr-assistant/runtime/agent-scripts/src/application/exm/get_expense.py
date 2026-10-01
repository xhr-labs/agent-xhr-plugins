"""Read one expense request in full (items, receipts, policy result, available actions)."""

from __future__ import annotations

from typing import Any

from src.application.exm.common import (
    as_args,
    base_url,
    call_json,
    entity_result,
    require_uuid,
    value,
)
from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext


def _strip_signed_urls(entity: Any) -> Any:
    """Drop short-lived signed receipt URLs.

    The agent must not hand out storage links: they expire, they bypass the app's
    own access checks, and the user downloads receipts from the Expense Management
    app instead. File names and document ids are kept so the answer can still name
    the attachment.
    """
    if isinstance(entity, list):
        return [_strip_signed_urls(item) for item in entity]
    if not isinstance(entity, dict):
        return entity
    return {
        key: _strip_signed_urls(item)
        for key, item in entity.items()
        if key not in ("signedUrl", "signed_url", "uploadUrl", "upload_url")
    }


async def run(task_args, context: RequestContext, http_client: HttpClient):
    args = as_args(task_args)

    expense_id, error = require_uuid(
        value(args, "expense_id", "expenseId", "id"),
        "expense_id",
        lookup_hint="skills/exm/list_my_expenses or skills/exm/list_expense_approvals",
    )
    if error:
        return error

    payload, failure = await call_json(
        http_client,
        "GET",
        f"{base_url(context)}/expenses/{expense_id}",
        headers=context.headers,
        params=None,
        feature="read this expense",
    )
    if failure:
        return failure

    return entity_result(_strip_signed_urls(payload))
