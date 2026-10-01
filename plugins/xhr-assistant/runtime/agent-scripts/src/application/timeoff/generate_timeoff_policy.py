from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
import json
import re
from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text
from src.shared.result import error_result, ok_result


ACTION_NAME = "timeoff_policy_setup"
JURISDICTION_ALIASES = {
    "AE": "UAE",
    "UAE": "UAE",
    "U_A_E": "UAE",
    "UAE_LABOUR_LAW": "UAE",
    "UAE_LABOR_LAW": "UAE",
    "UNITED_ARAB_EMIRATES": "UAE",
}
UAE_POLICY_DEFAULTS = {
    "name": "UAE Annual Leave Policy",
    "applied_location_name": "UAE",
    "employment_type_name": "Full-time",
    "block_probation_requests": True,
    "length_of_service_operator": "greater_than_or_equal",
    "length_of_service_value": 12,
    "length_of_service_unit": "MONTHS",
    "time_off_type_name": "Annual Leave",
    "period_allowance": "2.5",
    "accrual_period": "MONTHLY",
    "accrual_year_starts_on": "CALENDAR_YEAR",
    "accrual_timing": "START",
    "proration_strategy": "BY_DAYS",
}
ACCRUAL_PERIODS = {"MONTHLY", "YEARLY"}
ACCRUAL_YEAR_STARTS_ON = {"CALENDAR_YEAR", "EMPLOYEE_START"}
ACCRUAL_TIMINGS = {"START", "END"}
PRORATION_STRATEGIES = {"NONE", "BY_DAYS"}
CARRYOVER_EXPIRY_UNITS = {"DAYS", "MONTHS"}
LENGTH_OF_SERVICE_OPERATORS = {
    "EQUALS",
    "GREATER_THAN",
    "GREATER_THAN_OR_EQUAL",
    "LESS_THAN",
    "LESS_THAN_OR_EQUAL",
}
LENGTH_OF_SERVICE_OPERATOR_ALIASES = {
    "EQUAL": "EQUALS",
    "EQUAL_TO": "EQUALS",
    "AT_LEAST": "GREATER_THAN_OR_EQUAL",
    "MINIMUM": "GREATER_THAN_OR_EQUAL",
    "MINIMUM_OF": "GREATER_THAN_OR_EQUAL",
    "MORE_THAN": "GREATER_THAN",
    "OVER": "GREATER_THAN",
    "ABOVE": "GREATER_THAN",
    "AT_MOST": "LESS_THAN_OR_EQUAL",
    "MAXIMUM": "LESS_THAN_OR_EQUAL",
    "MAXIMUM_OF": "LESS_THAN_OR_EQUAL",
    "UP_TO": "LESS_THAN_OR_EQUAL",
    "NO_MORE_THAN": "LESS_THAN_OR_EQUAL",
    "UNDER": "LESS_THAN",
    "BELOW": "LESS_THAN",
}
LENGTH_OF_SERVICE_UNITS = {"DAYS", "MONTHS"}
LENGTH_OF_SERVICE_UNIT_ALIASES = {
    "DAY": "DAYS",
    "MONTH": "MONTHS",
}
EMPLOYEE_STATUSES = {"ACTIVE", "PROBATIONARY"}
EMPLOYEE_STATUS_ALIASES = {
    "ACTIVATED": "ACTIVE",
    "PROBATION": "PROBATIONARY",
}
GENDERS = {"MALE", "FEMALE", "OTHER", "NON_BINARY", "PREFER_NOT_TO_SAY", "UNSPECIFIED"}
GENDER_ALIASES = {
    "NONBINARY": "NON_BINARY",
}
SENIORITY_BONUS_PRORATIONS = {"BY_MONTHS", "BY_DAYS"}
SENIORITY_BONUS_ROUNDING_RULES = {"NONE", "UP_NEAREST_HALF", "UP_NEAREST_WHOLE"}
ROUNDING_RULE = "NONE"
CLIENT_CONTEXT_DATA_HEADER = "x-agent-client-context-data"


def _first_value(task_args: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in task_args and task_args[key] is not None:
            return task_args[key]
    return None


def _value_with_default(
    task_args: dict[str, Any],
    defaults: dict[str, Any],
    default_key: str,
    *keys: str,
) -> Any:
    value = _first_value(task_args, *keys)
    if value is not None:
        return value
    return defaults.get(default_key)


def _clean_structured_text(value: Any) -> str | None:
    text = clean_text(value)
    if not text:
        return None
    return text.rstrip(".,;:") or None


def _clean_enum(value: Any, supported: set[str]) -> str | None:
    text = _clean_structured_text(value)
    if not text:
        return None
    normalized = _normalize_enum_token(text)
    return normalized if normalized in supported else None


def _normalize_enum_token(value: str) -> str:
    return value.strip().upper().replace("-", "_").replace(" ", "_")


def _iter_scalar_values(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        values: list[Any] = []
        for item in value:
            values.extend(_iter_scalar_values(item))
        return values
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return [value]


def _clean_enum_values(
    value: Any,
    supported: set[str],
    aliases: dict[str, str] | None = None,
) -> list[str]:
    normalized_values: list[str] = []
    for item in _iter_scalar_values(value):
        text = _clean_structured_text(item)
        if not text:
            continue
        normalized = _normalize_enum_token(text)
        normalized = (aliases or {}).get(normalized, normalized)
        if normalized in supported and normalized not in normalized_values:
            normalized_values.append(normalized)
    return normalized_values


def _has_invalid_enum_values(
    value: Any,
    supported: set[str],
    aliases: dict[str, str] | None = None,
) -> bool:
    for item in _iter_scalar_values(value):
        text = _clean_structured_text(item)
        if not text:
            continue
        normalized = _normalize_enum_token(text)
        normalized = (aliases or {}).get(normalized, normalized)
        if normalized not in supported:
            return True
    return False


def _clean_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    text = _clean_structured_text(value)
    if not text:
        return None
    lowered = text.lower()
    if lowered in {"1", "true", "yes", "y", "on", "enabled"}:
        return True
    if lowered in {"0", "false", "no", "n", "off", "disabled"}:
        return False
    return None


def _clean_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, str):
        trimmed = _clean_structured_text(value)
        if not trimmed:
            return None
        try:
            return Decimal(trimmed)
        except InvalidOperation:
            return None
    return None


def _normalize_number(value: Decimal | None) -> int | float | None:
    if value is None:
        return None
    return int(value) if value == value.to_integral_value() else float(value)


def _normalize_positive_int(value: Decimal | None) -> int | None:
    if value is None:
        return None
    if value <= 0 or value != value.to_integral_value():
        return None
    return int(value)


def _normalize_non_negative_int(value: Decimal | None) -> int | None:
    if value is None:
        return None
    if value < 0 or value != value.to_integral_value():
        return None
    return int(value)


def _normalize_positive_number(value: Decimal | None) -> int | float | None:
    if value is None or value <= 0:
        return None
    return _normalize_number(value)


def _clean_length_of_service_operator(value: Any) -> str | None:
    text = _clean_structured_text(value)
    if not text:
        return None
    operator = _normalize_enum_token(text)
    operator = LENGTH_OF_SERVICE_OPERATOR_ALIASES.get(operator, operator)
    return operator.lower() if operator in LENGTH_OF_SERVICE_OPERATORS else None


def _clean_length_of_service_unit(value: Any) -> str | None:
    text = _clean_structured_text(value)
    if not text:
        return None
    unit = _normalize_enum_token(text)
    unit = LENGTH_OF_SERVICE_UNIT_ALIASES.get(unit, unit)
    return unit if unit in LENGTH_OF_SERVICE_UNITS else None


def _normalize_seniority_bonus_step(item: Any) -> dict[str, int | float] | None:
    if isinstance(item, dict):
        service_years_decimal = _clean_decimal(
            _first_value(item, "service_years", "serviceYears", "service_year", "years")
        )
        bonus_days_decimal = _clean_decimal(
            _first_value(item, "bonus_days", "bonusDays", "days")
        )
    else:
        text = _clean_structured_text(item)
        if not text:
            return None
        numbers = re.findall(r"\d+(?:\.\d+)?", text)
        if len(numbers) < 2:
            return None
        service_years_decimal = _clean_decimal(numbers[0])
        bonus_days_decimal = _clean_decimal(numbers[1])

    service_years = _normalize_positive_int(service_years_decimal)
    if service_years is None:
        return None
    if bonus_days_decimal is None or bonus_days_decimal <= 0:
        return None

    return {
        "service_years": service_years,
        "bonus_days": _normalize_number(bonus_days_decimal),
    }


def _normalize_seniority_bonus_steps(value: Any) -> tuple[list[dict[str, int | float]], bool]:
    if value is None:
        return [], False
    raw_items = value if isinstance(value, list) else [value]
    steps: list[dict[str, int | float]] = []
    for item in raw_items:
        step = _normalize_seniority_bonus_step(item)
        if step is None:
            return [], True
        steps.append(step)
    return steps, False


def _clean_date(value: Any) -> date | None:
    text = _clean_structured_text(value)
    if not text:
        return None
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def _clean_uuid_like(value: Any) -> str | None:
    text = _clean_structured_text(value)
    return text or None


def _client_context_data(context: RequestContext) -> dict[str, Any]:
    request_headers = context.request_headers if isinstance(context.request_headers, dict) else {}
    raw = request_headers.get(CLIENT_CONTEXT_DATA_HEADER)
    if not isinstance(raw, str) or not raw.strip():
        return {}
    try:
        parsed = json.loads(raw)
    except Exception:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _normalize_match_text(value: Any) -> str:
    return str(value or "").strip().lower().replace("-", " ").replace("_", " ")


def _iter_option_match_values(option: dict[str, Any]) -> list[str]:
    values: list[str] = []
    aliases = option.get("aliases")
    if isinstance(aliases, list):
        values.extend(str(item) for item in aliases if str(item or "").strip())
    match_text = option.get("match_text")
    if isinstance(match_text, str) and match_text.strip():
        values.extend(part.strip() for part in match_text.split("|") if part.strip())
    for key in (
        "label",
        "name",
        "city",
        "district",
        "street",
        "additional_street",
        "building_number",
        "zip_code",
        "country_name",
        "country_iso_code",
        "country_code",
        "location_type",
    ):
        value = option.get(key)
        if isinstance(value, str) and value.strip():
            values.append(value)
    return values


def _resolve_option(
    options: list[dict[str, Any]],
    *,
    raw_id: Any,
    raw_name: Any,
) -> tuple[str | None, str | None]:
    explicit_id = _clean_uuid_like(raw_id)
    if explicit_id:
        matched = next(
            (option for option in options if _clean_uuid_like(option.get("id")) == explicit_id),
            None,
        )
        if matched:
            canonical_name = clean_text(matched.get("name")) or clean_text(matched.get("label"))
            return explicit_id, canonical_name

    target = _normalize_match_text(raw_name)
    if not target:
        return None, None

    matches: list[dict[str, Any]] = []
    for option in options:
        option_values = {
            _normalize_match_text(value)
            for value in _iter_option_match_values(option)
        }
        option_values.discard("")
        if target in option_values:
            matches.append(option)

    if len(matches) != 1:
        return None, None

    matched = matches[0]
    return (
        _clean_uuid_like(matched.get("id")),
        clean_text(matched.get("name")) or clean_text(matched.get("label")),
    )


def _available_option_labels(options: list[dict[str, Any]]) -> list[str]:
    labels: list[str] = []
    for option in options:
        label = clean_text(option.get("label")) or clean_text(option.get("name"))
        if label and label not in labels:
            labels.append(label)
    return labels


def _location_clarification_result(
    *,
    requested_location: str,
    options: list[dict[str, Any]],
) -> dict[str, Any]:
    available_locations = _available_option_labels(options)
    if len(available_locations) == 1:
        message = (
            f'I can apply this policy to the available location "{available_locations[0]}". '
            "Is that the location you want?"
        )
    elif available_locations:
        joined = ", ".join(f'"{name}"' for name in available_locations)
        message = (
            f'I could not match "{requested_location}" to the available locations. '
            f"Which location do you want: {joined}?"
        )
    else:
        message = (
            f'I could not match "{requested_location}" to an available location. '
            "Which location should this policy apply to?"
        )

    return ok_result(
        {
            "clarification_required": True,
            "missing_field": "applied_location_id",
            "message": message,
            "requested_location": requested_location,
            "available_locations": available_locations,
        }
    )


def _clarification_error_result(error: str, user_message: str) -> dict[str, Any]:
    return {
        "ok": False,
        "error": error,
        "data": {
            "user_message": user_message,
        },
    }


async def run(task_args, context: RequestContext, http_client: HttpClient):
    del http_client

    task_args = task_args if isinstance(task_args, dict) else {}

    raw_jurisdiction = _first_value(
        task_args,
        "jurisdiction",
        "country",
        "country_code",
        "countryCode",
    )
    jurisdiction = None
    if raw_jurisdiction is not None:
        jurisdiction_token = _clean_structured_text(raw_jurisdiction)
        if jurisdiction_token:
            jurisdiction = JURISDICTION_ALIASES.get(_normalize_enum_token(jurisdiction_token))
        if not jurisdiction:
            return error_result("unsupported_timeoff_policy_jurisdiction")
    policy_defaults = UAE_POLICY_DEFAULTS if jurisdiction == "UAE" else {}

    name = clean_text(
        _value_with_default(task_args, policy_defaults, "name", "name", "policy_name", "policyName")
    )
    description = clean_text(
        _value_with_default(
            task_args,
            policy_defaults,
            "description",
            "description",
            "policy_description",
            "policyDescription",
        )
    )
    applied_location_id = _clean_uuid_like(
        _value_with_default(
            task_args,
            policy_defaults,
            "applied_location_id",
            "applied_location_id",
            "appliedLocationId",
            "location_id",
            "locationId",
        )
    )
    applied_location_name = clean_text(
        _value_with_default(
            task_args,
            policy_defaults,
            "applied_location_name",
            "applied_location_name",
            "appliedLocationName",
            "location_name",
            "locationName",
        )
    )
    employment_type_id = _clean_uuid_like(
        _value_with_default(
            task_args,
            policy_defaults,
            "employment_type_id",
            "employment_type_id",
            "employmentTypeId",
        )
    )
    employment_type_name = clean_text(
        _value_with_default(
            task_args,
            policy_defaults,
            "employment_type_name",
            "employment_type_name",
            "employmentTypeName",
        )
    )
    raw_employee_statuses = _first_value(
        task_args,
        "employee_statuses",
        "employeeStatuses",
        "employee_status",
        "employeeStatus",
    )
    employee_statuses = _clean_enum_values(
        raw_employee_statuses,
        EMPLOYEE_STATUSES,
        EMPLOYEE_STATUS_ALIASES,
    )
    raw_genders = _first_value(task_args, "genders", "gender")
    genders = _clean_enum_values(raw_genders, GENDERS, GENDER_ALIASES)
    block_probation_requests = _clean_bool(
        _value_with_default(
            task_args,
            policy_defaults,
            "block_probation_requests",
            "block_probation_requests",
            "blockProbationRequests",
            "block_probation",
            "blockProbation",
            "probation_requests_blocked",
            "probationRequestsBlocked",
        )
    )
    raw_length_of_service_operator = _first_value(
        task_args,
        "length_of_service_operator",
        "lengthOfServiceOperator",
        "service_length_operator",
        "serviceLengthOperator",
    )
    if raw_length_of_service_operator is None:
        raw_length_of_service_operator = policy_defaults.get("length_of_service_operator")
    length_of_service_operator = _clean_length_of_service_operator(
        raw_length_of_service_operator
    )
    raw_length_of_service_value = _first_value(
        task_args,
        "length_of_service_value",
        "lengthOfServiceValue",
        "length_of_service_days",
        "lengthOfServiceDays",
        "length_of_service_months",
        "lengthOfServiceMonths",
        "service_length_value",
        "serviceLengthValue",
        "service_days",
        "serviceDays",
        "service_months",
        "serviceMonths",
        "minimum_service_days",
        "minimumServiceDays",
        "minimum_service_months",
        "minimumServiceMonths",
    )
    if raw_length_of_service_value is None:
        raw_length_of_service_value = policy_defaults.get("length_of_service_value")
    length_of_service_value_decimal = _clean_decimal(raw_length_of_service_value)
    length_of_service_days = _normalize_non_negative_int(
        length_of_service_value_decimal
    )
    raw_length_of_service_unit = _first_value(
        task_args,
        "length_of_service_unit",
        "lengthOfServiceUnit",
        "length_of_service_units",
        "lengthOfServiceUnits",
        "service_length_unit",
        "serviceLengthUnit",
    )
    if raw_length_of_service_unit is None:
        raw_length_of_service_unit = policy_defaults.get("length_of_service_unit")
    length_of_service_unit = _clean_length_of_service_unit(raw_length_of_service_unit)
    if length_of_service_unit is None:
        if _first_value(
            task_args,
            "length_of_service_months",
            "lengthOfServiceMonths",
            "service_months",
            "serviceMonths",
            "minimum_service_months",
            "minimumServiceMonths",
        ) is not None:
            length_of_service_unit = "MONTHS"
        else:
            length_of_service_unit = "DAYS"
    time_off_type_id = _clean_uuid_like(
        _value_with_default(
            task_args,
            policy_defaults,
            "time_off_type_id",
            "time_off_type_id",
            "timeOffTypeId",
        )
    )
    time_off_type_name = clean_text(
        _value_with_default(
            task_args,
            policy_defaults,
            "time_off_type_name",
            "time_off_type_name",
            "timeOffTypeName",
        )
    )
    raw_annual_allowance = _first_value(task_args, "annual_allowance", "annualAllowance")
    raw_period_allowance = _first_value(
        task_args,
        "allowance",
        "period_allowance",
        "periodAllowance",
        "allowance_per_period",
        "allowancePerPeriod",
        "allowance_per_month",
        "allowancePerMonth",
        "monthly_allowance",
        "monthlyAllowance",
        "allowance_per_year",
        "allowancePerYear",
        "yearly_allowance",
        "yearlyAllowance",
    )
    if raw_annual_allowance is None and raw_period_allowance is None:
        raw_annual_allowance = policy_defaults.get("annual_allowance")
        raw_period_allowance = policy_defaults.get("period_allowance")
    annual_allowance = _clean_decimal(raw_annual_allowance)
    period_allowance = _clean_decimal(raw_period_allowance)
    period_allowance_is_invalid = (
        raw_period_allowance is not None and period_allowance is None
    )
    accrual_period = _clean_enum(
        _value_with_default(
            task_args,
            policy_defaults,
            "accrual_period",
            "accrual_period",
            "accrualPeriod",
        ),
        ACCRUAL_PERIODS,
    )
    accrual_year_starts_on = _clean_enum(
        _value_with_default(
            task_args,
            policy_defaults,
            "accrual_year_starts_on",
            "accrual_year_starts_on",
            "accrualYearStartsOn",
        ),
        ACCRUAL_YEAR_STARTS_ON,
    )
    accrual_timing = _clean_enum(
        _value_with_default(
            task_args,
            policy_defaults,
            "accrual_timing",
            "accrual_timing",
            "accrualTiming",
        ),
        ACCRUAL_TIMINGS,
    )
    proration_strategy = _clean_enum(
        _value_with_default(
            task_args,
            policy_defaults,
            "proration_strategy",
            "proration_strategy",
            "prorationStrategy",
            "proration",
        ),
        PRORATION_STRATEGIES,
    )
    if annual_allowance is None and period_allowance is not None and accrual_period:
        annual_allowance = (
            period_allowance * Decimal(12)
            if accrual_period == "MONTHLY"
            else period_allowance
        )
    effective_from = _clean_date(
        _first_value(task_args, "effective_from", "effectiveFrom", "effective_date", "effectiveDate")
    )
    effective_to = _clean_date(
        _first_value(task_args, "effective_to", "effectiveTo")
    )
    raw_retroactive_recalculation = _first_value(
        task_args,
        "retroactive_recalculation",
        "retroactiveRecalculation",
        "retroactive_enabled",
        "retroactiveEnabled",
    )
    retroactive_recalculation = _clean_bool(raw_retroactive_recalculation)
    retroactive_effective_from = _clean_date(
        _first_value(
            task_args,
            "retroactive_effective_from",
            "retroactiveEffectiveFrom",
            "recalculate_from",
            "recalculateFrom",
        )
    )
    reset_manual_balance_adjustments = _clean_bool(
        _first_value(
            task_args,
            "reset_manual_balance_adjustments",
            "resetManualBalanceAdjustments",
            "retroactive_reset_manual_balance_adjustments",
            "retroactiveResetManualBalanceAdjustments",
        )
    )
    reset_applied_policy_accruals = _clean_bool(
        _first_value(
            task_args,
            "reset_applied_policy_accruals",
            "resetAppliedPolicyAccruals",
            "retroactive_reset_applied_policy_accruals",
            "retroactiveResetAppliedPolicyAccruals",
        )
    )
    carryover_enabled = _clean_bool(
        _first_value(
            task_args,
            "carryover_enabled",
            "carryoverEnabled",
            "carry_over_enabled",
        )
    )
    carryover_max_days_decimal = _clean_decimal(
        _first_value(
            task_args,
            "carryover_max_days",
            "carryoverMaxDays",
            "carry_over_max_days",
        )
    )
    carryover_expiry_value_decimal = _clean_decimal(
        _first_value(
            task_args,
            "carryover_expiry_value",
            "carryoverExpiryValue",
            "carry_over_expiry_value",
        )
    )
    carryover_expiry_unit = _clean_enum(
        _first_value(
            task_args,
            "carryover_expiry_unit",
            "carryoverExpiryUnit",
            "carry_over_expiry_unit",
        ),
        CARRYOVER_EXPIRY_UNITS,
    )
    advance_leave_enabled = _clean_bool(
        _first_value(
            task_args,
            "advance_leave_enabled",
            "advanceLeaveEnabled",
            "allow_advance_leave",
            "allowAdvanceLeave",
            "negative_balance_enabled",
            "negativeBalanceEnabled",
        )
    )
    advance_leave_limit_days_decimal = _clean_decimal(
        _first_value(
            task_args,
            "advance_leave_limit_days",
            "advanceLeaveLimitDays",
            "advance_leave_max_days",
            "advanceLeaveMaxDays",
            "negative_balance_limit_days",
            "negativeBalanceLimitDays",
        )
    )
    seniority_bonus_enabled = _clean_bool(
        _first_value(
            task_args,
            "seniority_bonus_enabled",
            "seniorityBonusEnabled",
        )
    )
    raw_seniority_bonus_proration = _first_value(
        task_args,
        "seniority_bonus_proration",
        "seniorityBonusProration",
    )
    seniority_bonus_proration = _clean_enum(
        raw_seniority_bonus_proration,
        SENIORITY_BONUS_PRORATIONS,
    )
    raw_seniority_bonus_rounding_rule = _first_value(
        task_args,
        "seniority_bonus_rounding_rule",
        "seniorityBonusRoundingRule",
    )
    seniority_bonus_rounding_rule = _clean_enum(
        raw_seniority_bonus_rounding_rule,
        SENIORITY_BONUS_ROUNDING_RULES,
    )
    seniority_bonus_steps, invalid_seniority_bonus_steps = _normalize_seniority_bonus_steps(
        _first_value(
            task_args,
            "seniority_bonus_steps",
            "seniorityBonusSteps",
            "seniority_bonus_step",
            "seniorityBonusStep",
        )
    )

    carryover_max_days = _normalize_positive_int(carryover_max_days_decimal)
    carryover_expiry_value = _normalize_positive_int(carryover_expiry_value_decimal)
    advance_leave_limit_days = _normalize_positive_number(advance_leave_limit_days_decimal)

    if carryover_enabled is None:
        carryover_enabled = bool(carryover_max_days or carryover_expiry_value or carryover_expiry_unit)
    if advance_leave_enabled is None:
        advance_leave_enabled = bool(advance_leave_limit_days)
    if seniority_bonus_enabled is None:
        seniority_bonus_enabled = bool(
            seniority_bonus_steps
            or seniority_bonus_proration
            or seniority_bonus_rounding_rule
        )
    if retroactive_recalculation is None:
        retroactive_recalculation = bool(
            retroactive_effective_from
            or reset_manual_balance_adjustments
            or reset_applied_policy_accruals
        )
    if (
        raw_retroactive_recalculation is None
        and not retroactive_recalculation
        and effective_from is not None
        and date(date.today().year, 1, 1) <= effective_from < date.today()
    ):
        retroactive_recalculation = True
        if retroactive_effective_from is None:
            retroactive_effective_from = effective_from
    if retroactive_recalculation is None:
        retroactive_recalculation = False
    reset_manual_balance_adjustments = bool(reset_manual_balance_adjustments)
    reset_applied_policy_accruals = bool(reset_applied_policy_accruals)

    if retroactive_recalculation:
        if retroactive_effective_from is None:
            retroactive_effective_from = effective_from
        effective_from = retroactive_effective_from

    client_context_data = _client_context_data(context)
    timeoff_options = (
        client_context_data.get("timeoff_policy_options")
        if isinstance(client_context_data, dict)
        else None
    )
    if isinstance(timeoff_options, dict):
        location_options = [
            option
            for option in (timeoff_options.get("locations") or [])
            if isinstance(option, dict)
        ]
        location_id, canonical_location_name = _resolve_option(
            location_options,
            raw_id=applied_location_id,
            raw_name=applied_location_name,
        )
        if location_id:
            applied_location_id = location_id
            applied_location_name = canonical_location_name
        elif location_options and applied_location_name and not applied_location_id:
            return _location_clarification_result(
                requested_location=applied_location_name,
                options=location_options,
            )

        resolved_employment_type_id, canonical_employment_type_name = _resolve_option(
            [
                option
                for option in (timeoff_options.get("employment_types") or [])
                if isinstance(option, dict)
            ],
            raw_id=employment_type_id,
            raw_name=employment_type_name,
        )
        if resolved_employment_type_id:
            employment_type_id = resolved_employment_type_id
            employment_type_name = canonical_employment_type_name

        resolved_time_off_type_id, canonical_time_off_type_name = _resolve_option(
            [
                option
                for option in (timeoff_options.get("time_off_types") or [])
                if isinstance(option, dict)
            ],
            raw_id=time_off_type_id,
            raw_name=time_off_type_name,
        )
        if resolved_time_off_type_id:
            time_off_type_id = resolved_time_off_type_id
            time_off_type_name = canonical_time_off_type_name

    if not name:
        return error_result("timeoff_policy_name_required")
    if not applied_location_id and not applied_location_name:
        return error_result("timeoff_policy_applied_location_required")
    if not time_off_type_id and not time_off_type_name:
        return error_result("timeoff_policy_time_off_type_required")
    if period_allowance_is_invalid:
        return error_result("timeoff_policy_allowance_must_be_positive")
    if annual_allowance is None:
        return error_result("timeoff_policy_annual_allowance_required")
    if annual_allowance <= 0:
        return error_result("timeoff_policy_annual_allowance_must_be_positive")
    if _has_invalid_enum_values(raw_employee_statuses, EMPLOYEE_STATUSES, EMPLOYEE_STATUS_ALIASES):
        return error_result("timeoff_policy_employee_statuses_invalid")
    if _has_invalid_enum_values(raw_genders, GENDERS, GENDER_ALIASES):
        return error_result("timeoff_policy_genders_invalid")
    if raw_length_of_service_operator is not None and length_of_service_operator is None:
        return error_result("timeoff_policy_length_of_service_operator_invalid")
    if raw_length_of_service_unit is not None and _clean_length_of_service_unit(
        raw_length_of_service_unit
    ) is None:
        return error_result("timeoff_policy_length_of_service_unit_invalid")
    if raw_length_of_service_value is not None and length_of_service_days is None:
        return error_result("timeoff_policy_length_of_service_days_must_be_non_negative_integer")
    if length_of_service_days is not None and length_of_service_operator is None:
        return error_result("timeoff_policy_length_of_service_operator_required")
    if length_of_service_operator is not None and length_of_service_days is None:
        return error_result("timeoff_policy_length_of_service_days_required")
    if not accrual_period:
        return error_result("invalid_accrual_period")
    if not accrual_year_starts_on:
        return error_result("invalid_accrual_year_starts_on")
    if not proration_strategy:
        return error_result("invalid_proration_strategy")
    if retroactive_recalculation and retroactive_effective_from is None:
        return _clarification_error_result(
            "timeoff_policy_retroactive_effective_from_required",
            "What recalculation-from date should this retroactive Time Off policy use?",
        )
    if effective_from is None:
        return _clarification_error_result(
            "timeoff_policy_effective_from_required",
            "What effective-from date should this Time Off policy use?",
        )
    if retroactive_recalculation and effective_from < date(date.today().year, 1, 1):
        return _clarification_error_result(
            "timeoff_policy_retroactive_effective_from_out_of_cycle",
            "Retroactive recalculation must start within the current calendar year. What recalculation-from date should this Time Off policy use?",
        )
    if retroactive_recalculation and effective_from > date.today():
        return _clarification_error_result(
            "timeoff_policy_retroactive_effective_from_cannot_be_in_the_future",
            "The retroactive recalculation date cannot be in the future. What recalculation-from date should this Time Off policy use?",
        )
    if not retroactive_recalculation and effective_from < date.today():
        return _clarification_error_result(
            "timeoff_policy_effective_from_cannot_be_in_the_past",
            "The effective-from date must be today or a future date. What effective-from date should this Time Off policy use?",
        )
    if effective_to is not None and effective_to < effective_from:
        return error_result("timeoff_policy_effective_to_cannot_be_before_effective_from")
    if carryover_max_days_decimal is not None and carryover_max_days is None:
        return error_result("timeoff_policy_carryover_max_days_must_be_positive_integer")
    if carryover_expiry_value_decimal is not None and carryover_expiry_value is None:
        return error_result("timeoff_policy_carryover_expiry_value_must_be_positive_integer")
    if (carryover_expiry_value is None) != (carryover_expiry_unit is None):
        return error_result("timeoff_policy_carryover_expiry_value_and_unit_required")
    if advance_leave_limit_days_decimal is not None and advance_leave_limit_days is None:
        return error_result("timeoff_policy_advance_leave_limit_days_must_be_positive")
    if advance_leave_enabled and advance_leave_limit_days is None:
        return error_result("timeoff_policy_advance_leave_limit_days_required")
    if raw_seniority_bonus_proration is not None and seniority_bonus_proration is None:
        return error_result("timeoff_policy_seniority_bonus_proration_invalid")
    if raw_seniority_bonus_rounding_rule is not None and seniority_bonus_rounding_rule is None:
        return error_result("timeoff_policy_seniority_bonus_rounding_rule_invalid")
    if invalid_seniority_bonus_steps:
        return error_result("timeoff_policy_seniority_bonus_steps_invalid")
    if seniority_bonus_enabled and not seniority_bonus_steps:
        return error_result("timeoff_policy_seniority_bonus_steps_required")
    seniority_bonus_service_years = [step["service_years"] for step in seniority_bonus_steps]
    if len(seniority_bonus_service_years) != len(set(seniority_bonus_service_years)):
        return error_result("timeoff_policy_seniority_bonus_service_years_duplicate")

    if not carryover_enabled:
        carryover_max_days = None
        carryover_expiry_value = None
        carryover_expiry_unit = None
    if not advance_leave_enabled:
        advance_leave_limit_days = None
    if block_probation_requests is None:
        block_probation_requests = True
    if seniority_bonus_enabled:
        seniority_bonus_proration = seniority_bonus_proration or "BY_MONTHS"
        seniority_bonus_rounding_rule = seniority_bonus_rounding_rule or "NONE"
    else:
        seniority_bonus_steps = []
        seniority_bonus_proration = None
        seniority_bonus_rounding_rule = None

    if accrual_period == "MONTHLY":
        if not accrual_timing:
            return error_result("timeoff_policy_accrual_timing_required_for_monthly")
    else:
        accrual_timing = accrual_timing or "START"

    payload = {
        "name": name,
        "description": description,
        "applied_location_id": applied_location_id,
        "applied_location_name": applied_location_name,
        "employment_type_id": employment_type_id,
        "employment_type_name": employment_type_name,
        "employee_statuses": employee_statuses,
        "genders": genders,
        "block_probation_requests": block_probation_requests,
        "length_of_service_operator": length_of_service_operator,
        "length_of_service_days": length_of_service_days,
        "length_of_service_unit": length_of_service_unit,
        "time_off_type_id": time_off_type_id,
        "time_off_type_name": time_off_type_name,
        "annual_allowance": _normalize_number(annual_allowance),
        "accrual_period": accrual_period,
        "accrual_year_starts_on": accrual_year_starts_on,
        "accrual_timing": accrual_timing,
        "proration_strategy": proration_strategy,
        "rounding_rule": ROUNDING_RULE,
        "effective_from": effective_from.isoformat(),
        "effective_to": effective_to.isoformat() if effective_to else None,
        "retroactive_recalculation": retroactive_recalculation,
        "retroactive_effective_from": (
            retroactive_effective_from.isoformat()
            if retroactive_effective_from
            else None
        ),
        "reset_manual_balance_adjustments": reset_manual_balance_adjustments,
        "reset_applied_policy_accruals": reset_applied_policy_accruals,
        "carryover_enabled": carryover_enabled,
        "carryover_max_days": carryover_max_days,
        "carryover_expiry_value": carryover_expiry_value,
        "carryover_expiry_unit": carryover_expiry_unit,
        "advance_leave_enabled": advance_leave_enabled,
        "advance_leave_limit_days": advance_leave_limit_days,
        "seniority_bonus_enabled": seniority_bonus_enabled,
        "seniority_bonus_proration": seniority_bonus_proration,
        "seniority_bonus_rounding_rule": seniority_bonus_rounding_rule,
        "seniority_bonus_steps": seniority_bonus_steps,
    }

    return ok_result({"content": payload, "action": ACTION_NAME})
