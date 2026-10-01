"""List the caller's own expense requests (``My Expenses`` screen)."""

from __future__ import annotations

from src.application.exm.common import (
    as_args,
    base_url,
    call_json,
    date_range,
    list_result,
    normalize_statuses,
    optional_uuid,
    paging,
    value,
)
from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text


async def run(task_args, context: RequestContext, http_client: HttpClient):
    args = as_args(task_args)

    statuses, error = normalize_statuses(value(args, "status", "statuses"))
    if error:
        return error

    date_from, date_to, error = date_range(args)
    if error:
        return error

    category_id, error = optional_uuid(
        value(args, "category_id", "categoryId"),
        "category_id",
        lookup_hint="skills/exm/list_expense_categories",
    )
    if error:
        return error

    params = paging(args)
    if statuses:
        params["status"] = statuses
    if date_from:
        params["dateFrom"] = date_from
    if date_to:
        params["dateTo"] = date_to
    if category_id:
        params["categoryId"] = category_id
    keyword = clean_text(value(args, "keyword", "search"))
    if keyword:
        params["keyword"] = keyword
    sort = clean_text(value(args, "sort"))
    if sort:
        params["sort"] = sort

    payload, failure = await call_json(
        http_client,
        "GET",
        f"{base_url(context)}/expenses/my",
        headers=context.headers,
        params=params,
        feature="read their own expenses",
    )
    if failure:
        return failure

    return list_result(
        payload,
        "expenses",
        filters={
            "statuses": statuses,
            "date_from": date_from,
            "date_to": date_to,
            "category_id": category_id,
            "keyword": keyword,
        },
    )
