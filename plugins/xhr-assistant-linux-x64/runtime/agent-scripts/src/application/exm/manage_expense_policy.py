"""Create, edit, enable, archive, delete, or dry-run an expense policy.

The Expense Management policy engine evaluates submitted expenses against ordered rules.
This tool exposes the same operations as the Policies screen, plus the two read-only
evaluations the screen runs before saving (conflict check and policy preview).
"""

from __future__ import annotations

from typing import Any

from src.application.exm.common import (
    as_args,
    base_url,
    call_json,
    entity_result,
    iso_date,
    parse_json_array,
    parse_json_object,
    require_enum,
    require_uuid,
    value,
    write_headers,
)
from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_float, clean_int, clean_text, to_bool
from src.shared.result import error_result, ok_result


ACTIONS = (
    "create",
    "update",
    "enable",
    "disable",
    "archive",
    "delete",
    "check_conflict",
    "evaluate_preview",
)

RULE_TYPES = (
    "CATEGORY_ACCESS",
    "AMOUNT_LIMIT",
    "RECEIPT_REQUIRED",
    "DESCRIPTION_REQUIRED",
    "SUBMISSION_WINDOW",
    "FUTURE_DATE_BLOCKED",
    "CLIENT_REQUIRED",
    "PROJECT_REQUIRED",
    "ATTENDEES_REQUIRED",
    "MERCHANT_REQUIRED",
    "MERCHANT_RESTRICTION",
    "PAYMENT_METHOD_RESTRICTION",
    "FLIGHT_CABIN_RESTRICTION",
    "MILEAGE_RATE",
    "PER_NIGHT_LIMIT",
    "PER_ATTENDEE_LIMIT",
)
SEVERITIES = ("HARD_BLOCK", "SOFT_WARNING", "INFO")
PERIODS = (
    "PER_EXPENSE",
    "PER_DAY",
    "PER_WEEK",
    "PER_MONTH",
    "PER_QUARTER",
    "PER_YEAR",
    "PER_TRIP",
    "PER_NIGHT",
    "PER_ATTENDEE",
    "PER_DISTANCE_UNIT",
)
ACCESS_VALUES = ("ALLOWED", "NOT_ALLOWED", "ALLOWED_WITH_WARNING")
ELIGIBILITY_KEYS = ("all", "any", "none")


def _pick(item: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if item.get(key) is not None:
            return item[key]
    return None


def _enum(item: dict[str, Any], keys: tuple[str, ...], name: str, allowed: tuple[str, ...], index: int):
    raw = _pick(item, *keys)
    text = clean_text(raw)
    if not text:
        return None, None
    for option in allowed:
        if text.upper() == option.upper():
            return option, None
    return None, error_result(
        f"rules_json_invalid: rule {index} has {name} '{text}'. Allowed values: {', '.join(allowed)}."
    )


def _rules(raw: Any) -> tuple[list[dict[str, Any]] | None, dict[str, Any] | None]:
    """Normalize the rule array the caller supplies into the backend snake_case shape."""
    items, error = parse_json_array(raw, "rules_json")
    if error:
        return None, error
    if items is None:
        return None, None

    rules: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            return None, error_result(f"rules_json_invalid: rule {index} must be a JSON object.")

        rule_type, error = _enum(item, ("ruleType", "rule_type"), "ruleType", RULE_TYPES, index)
        if error:
            return None, error
        if not rule_type:
            return None, error_result(f"rules_json_invalid: rule {index} is missing ruleType.")

        severity, error = _enum(item, ("severity",), "severity", SEVERITIES, index)
        if error:
            return None, error
        period, error = _enum(item, ("period",), "period", PERIODS, index)
        if error:
            return None, error
        access, error = _enum(item, ("access",), "access", ACCESS_VALUES, index)
        if error:
            return None, error

        rule: dict[str, Any] = {
            "rule_type": rule_type,
            "severity": severity or "SOFT_WARNING",
            "period": period or "PER_EXPENSE",
            "category_id": clean_text(_pick(item, "categoryId", "category_id")),
            "access": access,
            "limit_amount": clean_float(_pick(item, "limitAmount", "limit_amount")),
            "limit_currency": (clean_text(_pick(item, "limitCurrency", "limit_currency")) or None),
            "threshold_amount": clean_float(_pick(item, "thresholdAmount", "threshold_amount")),
            "threshold_currency": (
                clean_text(_pick(item, "thresholdCurrency", "threshold_currency")) or None
            ),
            "sort_order": clean_int(_pick(item, "sortOrder", "sort_order")) or index,
            "enabled": to_bool(_pick(item, "enabled")) if _pick(item, "enabled") is not None else True,
            "message": clean_text(item.get("message")),
            "metadata": item.get("metadata") if isinstance(item.get("metadata"), dict) else {},
        }
        rule_id = clean_text(item.get("id"))
        if rule_id:
            rule["id"] = rule_id

        if rule_type == "AMOUNT_LIMIT" and rule["limit_amount"] is None:
            return None, error_result(
                f"rules_json_invalid: rule {index} is AMOUNT_LIMIT and needs limitAmount."
            )
        if rule_type == "CATEGORY_ACCESS" and not rule["access"]:
            return None, error_result(
                f"rules_json_invalid: rule {index} is CATEGORY_ACCESS and needs access "
                f"({', '.join(ACCESS_VALUES)})."
            )
        if rule["threshold_amount"] is not None and not rule["threshold_currency"]:
            return None, error_result(
                f"rules_json_invalid: rule {index} sets thresholdAmount, so thresholdCurrency is required."
            )
        rules.append(rule)
    return rules, None


def _eligibility(raw: Any) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    expression, error = parse_json_object(raw, "eligibility_json")
    if error:
        return None, error
    if expression is None:
        return None, None
    unknown = [key for key in expression if key not in ELIGIBILITY_KEYS]
    if unknown:
        return None, error_result(
            f"eligibility_json_invalid: unknown key(s) {', '.join(unknown)}. "
            f"Allowed keys: {', '.join(ELIGIBILITY_KEYS)}."
        )
    compacted: dict[str, Any] = {}
    for key in ELIGIBILITY_KEYS:
        conditions = expression.get(key)
        if not isinstance(conditions, list):
            compacted[key] = []
            continue
        compacted[key] = [
            condition
            for condition in conditions
            if isinstance(condition, dict) and clean_text(condition.get("field"))
        ]
    return compacted, None


def _policy_body(args: dict[str, Any], *, require_name: bool):
    body: dict[str, Any] = {}

    name = clean_text(value(args, "name"))
    if name:
        body["name"] = name
    elif require_name:
        return None, error_result("name_required: a policy needs a name.")

    description = clean_text(value(args, "description"))
    if description is not None:
        body["description"] = description

    raw_enabled = value(args, "enabled")
    if raw_enabled is not None:
        body["enabled"] = to_bool(raw_enabled)

    priority = clean_int(value(args, "priority"))
    if priority is not None:
        body["priority"] = priority

    effective_from, error = iso_date(value(args, "effective_from", "effectiveFrom"), "effective_from")
    if error:
        return None, error
    effective_to, error = iso_date(value(args, "effective_to", "effectiveTo"), "effective_to")
    if error:
        return None, error
    if effective_from and effective_to and effective_from > effective_to:
        return None, error_result("invalid_period: effective_to must be on or after effective_from.")
    if effective_from:
        body["effective_from"] = effective_from
    if effective_to:
        body["effective_to"] = effective_to

    eligibility, error = _eligibility(value(args, "eligibility_json", "eligibilityJson"))
    if error:
        return None, error
    if eligibility is not None:
        body["eligibility_expression"] = eligibility

    rules, error = _rules(value(args, "rules_json", "rulesJson"))
    if error:
        return None, error
    if rules is not None:
        body["rules"] = rules

    if require_name:
        if "effective_from" not in body:
            return None, error_result("effective_from_required: pass --effective-from YYYY-MM-DD.")
        if not body.get("rules"):
            return None, error_result("rules_required: a policy needs at least one rule in --rules-json.")
        body.setdefault("eligibility_expression", {"all": [], "any": [], "none": []})
        body.setdefault("enabled", True)
        body.setdefault("priority", 100)
    elif not body:
        return None, error_result(
            "no_changes: pass at least one field to update, for example --name or --rules-json."
        )

    return body, None


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

    root = f"{base_url(context)}/policies"
    headers = write_headers(context, args)
    feature = "manage expense policies"

    if action == "evaluate_preview":
        preview, error = parse_json_object(value(args, "preview_json", "previewJson"), "preview_json")
        if error:
            return error
        if not preview:
            return error_result(
                "preview_json_required: pass --preview-json with the draft expense to evaluate."
            )
        payload, failure = await call_json(
            http_client,
            "POST",
            f"{root}/evaluate-preview",
            headers=context.headers,
            body=preview,
            feature="preview expense policy results",
        )
        if failure:
            return failure
        return entity_result(payload, action=action)

    if action == "check_conflict":
        body, error = _policy_body(args, require_name=True)
        if error:
            return error
        # A conflict check for an existing policy must exclude that policy from the
        # overlap search, so the id is optional here and only sent when editing.
        raw_policy_id = clean_text(value(args, "policy_id", "policyId", "id"))
        if raw_policy_id:
            policy_id, error = require_uuid(
                raw_policy_id,
                "policy_id",
                lookup_hint="skills/exm/list_expense_policies",
            )
            if error:
                return error
            body["policy_id"] = policy_id
        payload, failure = await call_json(
            http_client,
            "POST",
            f"{root}/check-conflict",
            headers=context.headers,
            body=body,
            feature="check expense policy conflicts",
        )
        if failure:
            return failure
        return entity_result(payload, action=action)

    if action == "create":
        body, error = _policy_body(args, require_name=True)
        if error:
            return error
        payload, failure = await call_json(
            http_client, "POST", root, headers=headers, body=body, feature=feature
        )
        if failure:
            return failure
        return entity_result(payload, action=action)

    policy_id, error = require_uuid(
        value(args, "policy_id", "policyId", "id"),
        "policy_id",
        lookup_hint="skills/exm/list_expense_policies",
    )
    if error:
        return error

    if action == "update":
        body, error = _policy_body(args, require_name=False)
        if error:
            return error
        payload, failure = await call_json(
            http_client, "PATCH", f"{root}/{policy_id}", headers=headers, body=body, feature=feature
        )
        if failure:
            return failure
        return entity_result(payload, action=action, policy_id=policy_id)

    if action in ("enable", "disable"):
        payload, failure = await call_json(
            http_client,
            "PATCH",
            f"{root}/{policy_id}/enabled",
            headers=headers,
            body={"enabled": action == "enable"},
            feature=feature,
        )
        if failure:
            return failure
        return entity_result(payload, action=action, policy_id=policy_id)

    if action == "archive":
        payload, failure = await call_json(
            http_client, "POST", f"{root}/{policy_id}/archive", headers=headers, feature=feature
        )
        if failure:
            return failure
        return entity_result(payload, action=action, policy_id=policy_id)

    payload, failure = await call_json(
        http_client, "DELETE", f"{root}/{policy_id}", headers=headers, feature=feature
    )
    if failure:
        return failure
    return ok_result({"action": action, "policy_id": policy_id, "deleted": True})
