"""Read expense categories, one category's activity log, or its deletion eligibility."""

from __future__ import annotations

from src.application.exm.common import (
    as_args,
    base_url,
    call_json,
    entity_result,
    list_result,
    require_enum,
    require_uuid,
    value,
)
from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext


VIEWS = ("list", "activity_logs", "deletion_eligibility")


async def run(task_args, context: RequestContext, http_client: HttpClient):
    args = as_args(task_args)

    raw_view = value(args, "view")
    if isinstance(raw_view, str):
        raw_view = raw_view.replace("-", "_")
    view, error = require_enum(raw_view, "view", VIEWS)
    if error:
        return error
    view = view or "list"

    root = f"{base_url(context)}/categories"

    if view == "list":
        payload, failure = await call_json(
            http_client,
            "GET",
            root,
            headers=context.headers,
            params=None,
            feature="read expense categories",
        )
        if failure:
            return failure
        return list_result(payload, "categories", view=view)

    category_id, error = require_uuid(
        value(args, "category_id", "categoryId", "id"),
        "category_id",
        lookup_hint="skills/exm/list_expense_categories with the default --view list",
    )
    if error:
        return error

    path = "activity-logs" if view == "activity_logs" else "deletion-eligibility"
    payload, failure = await call_json(
        http_client,
        "GET",
        f"{root}/{category_id}/{path}",
        headers=context.headers,
        params=None,
        feature="read expense category configuration",
    )
    if failure:
        return failure

    if view == "activity_logs":
        return list_result(payload, "activity_logs", view=view, category_id=category_id)
    return entity_result(payload, view=view, category_id=category_id)
