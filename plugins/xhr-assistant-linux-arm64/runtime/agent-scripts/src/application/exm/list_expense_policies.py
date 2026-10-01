"""Read expense policies: the policy list, or one policy with its eligibility and rules."""

from __future__ import annotations

from src.application.exm.common import (
    POLICY_STATUSES,
    as_args,
    base_url,
    call_json,
    entity_result,
    list_result,
    optional_uuid,
    paging,
    require_enum,
    value,
)
from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text, to_bool


async def run(task_args, context: RequestContext, http_client: HttpClient):
    args = as_args(task_args)

    policy_id, error = optional_uuid(
        value(args, "policy_id", "policyId", "id"),
        "policy_id",
        lookup_hint="skills/exm/list_expense_policies without --policy-id",
    )
    if error:
        return error

    root = f"{base_url(context)}/policies"

    if policy_id:
        payload, failure = await call_json(
            http_client,
            "GET",
            f"{root}/{policy_id}",
            headers=context.headers,
            params=None,
            feature="read expense policies",
        )
        if failure:
            return failure
        return entity_result(payload, policy_id=policy_id)

    status, error = require_enum(value(args, "status"), "status", POLICY_STATUSES)
    if error:
        return error

    params = paging(args)
    if status:
        params["status"] = status
    # `--enabled` arrives as a real bool from the CLI parser and as a string when the
    # runtime injects TASK_ARGS, so both shapes have to be accepted here.
    raw_enabled = value(args, "enabled")
    if isinstance(raw_enabled, bool):
        params["enabled"] = raw_enabled
    elif clean_text(raw_enabled) is not None:
        params["enabled"] = to_bool(raw_enabled)
    keyword = clean_text(value(args, "keyword", "search"))
    if keyword:
        params["keyword"] = keyword

    payload, failure = await call_json(
        http_client,
        "GET",
        root,
        headers=context.headers,
        params=params,
        feature="read expense policies",
    )
    if failure:
        return failure

    return list_result(payload, "policies", filters={"status": status, "keyword": keyword})
