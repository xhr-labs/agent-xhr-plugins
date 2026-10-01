"""Read the caller's expense approval queue: pending items, decision history, or counts."""

from __future__ import annotations

from src.application.exm.common import (
    as_args,
    base_url,
    call_json,
    entity_result,
    list_result,
    normalize_statuses,
    paging,
    require_enum,
    value,
)
from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text


VIEWS = ("pending", "history", "count")


async def run(task_args, context: RequestContext, http_client: HttpClient):
    args = as_args(task_args)

    view, error = require_enum(value(args, "view"), "view", VIEWS)
    if error:
        return error
    view = view or "pending"

    root = f"{base_url(context)}/expenses/approvals"

    if view == "count":
        payload, failure = await call_json(
            http_client,
            "GET",
            f"{root}/count",
            headers=context.headers,
            params=None,
            feature="read the expense approval counters",
        )
        if failure:
            return failure
        return entity_result(payload, view="count")

    params = paging(args)

    if view == "history":
        statuses, error = normalize_statuses(value(args, "status", "statuses"))
        if error:
            return error
        if statuses:
            params["status.in"] = ",".join(statuses)
        keyword = clean_text(value(args, "keyword", "search"))
        if keyword:
            params["keyword"] = keyword
        url = f"{root}/history"
        feature = "read the expense approval history"
    else:
        url = root
        feature = "read the expense approval queue"

    payload, failure = await call_json(
        http_client,
        "GET",
        url,
        headers=context.headers,
        params=params,
        feature=feature,
    )
    if failure:
        return failure

    return list_result(payload, "expenses", view=view)
