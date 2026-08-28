from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text, is_uuid, normalize_list
from src.shared.result import error_result, ok_result


ACTION_NAME = "attendance_overtime_policy_setup"
TRIGGER_UNITS = {"DAILY", "WEEKLY"}
THRESHOLD_BEHAVIORS = {"PROGRESSIVE", "CLIFF"}
THRESHOLD_SOURCES = {"SHIFT_TARGET", "FIXED"}
CALCULATION_MODES = {
    "POSITIVE_OVERTIME_ONLY",
    "TIME_BALANCE",
    "FLEXIBLE_TIME_BALANCE",
}
REST_DAY_COMPENSATION_MODES = {
    "NONE",
    "PAY_PREMIUM",
    "COMPENSATORY_DAY",
    "HR_CHOICE",
}
JURISDICTION_ALIASES = {
    "AE": "UAE",
    "UAE": "UAE",
    "U_A_E": "UAE",
    "UAE_LABOUR_LAW": "UAE",
    "UAE_LABOR_LAW": "UAE",
    "UNITED_ARAB_EMIRATES": "UAE",
}
UAE_POLICY_DEFAULTS = {
    "name": "UAE Overtime Compliance Policy",
    "enabled": True,
    "trigger_unit": "DAILY",
    "threshold_behavior": "PROGRESSIVE",
    "threshold_source": "SHIFT_TARGET",
    "calculation_mode": "POSITIVE_OVERTIME_ONLY",
    "negative_balance_limit_minutes": None,
    "threshold_hours": None,
    "weekdays_only": False,
    "weekends_only": False,
    "max_daily_overtime_hours": 2,
    "max_daily_overtime_percent_of_normal_hours": None,
    "max_total_daily_hours": 10,
    "max_monthly_overtime_hours": None,
    "max_yearly_overtime_hours": None,
    "max_extended_yearly_overtime_hours": None,
    "work_location_ids": [],
    "max_total_hours_window_weeks": 3,
    "max_total_hours_per_window": 144,
    "night_window_enabled": True,
    "night_window_start": "22:00:00",
    "night_window_end": "04:00:00",
    "night_premium_shift_worker_exclusion_enabled": True,
    "rest_day_compensation_mode": "HR_CHOICE",
    "max_consecutive_rest_day_work_days": 2,
    "day_worker_rest_day_sequence_exemption_enabled": False,
}
CAP_FIELDS = {
    "max_daily_overtime_hours": ("max_daily_overtime_hours", "maxDailyOvertimeHours"),
    "max_daily_overtime_percent_of_normal_hours": (
        "max_daily_overtime_percent_of_normal_hours",
        "maxDailyOvertimePercentOfNormalHours",
    ),
    "max_total_daily_hours": ("max_total_daily_hours", "maxTotalDailyHours"),
    "max_monthly_overtime_hours": ("max_monthly_overtime_hours", "maxMonthlyOvertimeHours"),
    "max_yearly_overtime_hours": ("max_yearly_overtime_hours", "maxYearlyOvertimeHours"),
    "max_extended_yearly_overtime_hours": (
        "max_extended_yearly_overtime_hours",
        "maxExtendedYearlyOvertimeHours",
    ),
}


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


def _clean_bool(value: Any, default: bool | None = None) -> bool | None:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        lowered = value.strip().lower()
        if not lowered:
            return default
        if lowered in {"1", "true", "yes", "y", "on"}:
            return True
        if lowered in {"0", "false", "no", "n", "off"}:
            return False
    return default


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
        trimmed = value.strip()
        if not trimmed:
            return None
        try:
            return Decimal(trimmed)
        except InvalidOperation:
            return None
    return None


def _clean_int(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if value.is_integer() else None
    if isinstance(value, str):
        trimmed = value.strip()
        if not trimmed:
            return None
        try:
            return int(trimmed)
        except ValueError:
            return None
    return None


def _normalize_number(value: Decimal | None) -> int | float | None:
    if value is None:
        return None
    return int(value) if value == value.to_integral_value() else float(value)


def _clean_time(value: Any) -> str | None:
    text = clean_text(value)
    if not text:
        return None
    parts = text.split(":")
    if len(parts) not in {2, 3}:
        return None
    if not all(part.isdigit() for part in parts):
        return None

    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = int(parts[2]) if len(parts) == 3 else 0

    if hours < 0 or hours > 23:
        return None
    if minutes < 0 or minutes > 59:
        return None
    if seconds < 0 or seconds > 59:
        return None

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def _clean_enum(value: Any, supported: set[str]) -> str | None:
    text = clean_text(value)
    if not text:
        return None
    normalized = text.upper().replace("-", "_").replace(" ", "_")
    return normalized if normalized in supported else None


def _clean_jurisdiction(value: Any) -> str | None:
    text = clean_text(value)
    if not text:
        return None
    normalized = text.upper().replace("-", "_").replace(" ", "_").replace(".", "")
    return JURISDICTION_ALIASES.get(normalized)


def _clean_work_location_ids_with_defaults(
    task_args: dict[str, Any],
    defaults: dict[str, Any],
) -> tuple[list[str], str | None]:
    raw_value = _value_with_default(
        task_args,
        defaults,
        "work_location_ids",
        "work_location_ids",
        "workLocationIds",
        "work_locations",
        "workLocations",
        "location_ids",
        "locationIds",
    )
    work_location_ids = normalize_list(raw_value)
    if not work_location_ids:
        return [], None

    normalized: list[str] = []
    seen: set[str] = set()
    for work_location_id in work_location_ids:
        if not is_uuid(work_location_id):
            return [], "invalid_work_location_id"
        if work_location_id in seen:
            return [], "duplicate_work_location_ids"
        seen.add(work_location_id)
        normalized.append(work_location_id)

    return normalized, None


async def run(task_args, context: RequestContext, http_client: HttpClient):
    task_args = task_args if isinstance(task_args, dict) else {}

    jurisdiction_raw = _first_value(
        task_args,
        "jurisdiction",
        "country",
        "country_code",
        "countryCode",
        "legal_jurisdiction",
        "legalJurisdiction",
    )
    jurisdiction = _clean_jurisdiction(jurisdiction_raw)
    if jurisdiction_raw is not None and not jurisdiction:
        return error_result("invalid_jurisdiction")
    policy_defaults = UAE_POLICY_DEFAULTS if jurisdiction == "UAE" else {}

    name = clean_text(
        _value_with_default(task_args, policy_defaults, "name", "name", "policy_name", "policyName")
    )
    description = clean_text(
        _first_value(task_args, "description", "policy_description", "policyDescription")
    )
    enabled = _clean_bool(
        _value_with_default(task_args, policy_defaults, "enabled", "enabled", "is_enabled", "isEnabled"),
        default=True,
    )
    trigger_unit = _clean_enum(
        _value_with_default(task_args, policy_defaults, "trigger_unit", "trigger_unit", "triggerUnit"),
        TRIGGER_UNITS,
    )
    threshold_behavior = _clean_enum(
        _value_with_default(
            task_args,
            policy_defaults,
            "threshold_behavior",
            "threshold_behavior",
            "thresholdBehavior",
        ),
        THRESHOLD_BEHAVIORS,
    )
    threshold_source = _clean_enum(
        _value_with_default(task_args, policy_defaults, "threshold_source", "threshold_source", "thresholdSource"),
        THRESHOLD_SOURCES,
    )
    threshold_hours = _clean_decimal(
        _value_with_default(task_args, policy_defaults, "threshold_hours", "threshold_hours", "thresholdHours")
    )
    calculation_mode_raw = _value_with_default(
        task_args,
        policy_defaults,
        "calculation_mode",
        "calculation_mode",
        "calculationMode",
    )
    calculation_mode = _clean_enum(calculation_mode_raw, CALCULATION_MODES)
    negative_balance_limit_minutes_raw = _value_with_default(
        task_args,
        policy_defaults,
        "negative_balance_limit_minutes",
        "negative_balance_limit_minutes",
        "negativeBalanceLimitMinutes",
    )
    negative_balance_limit_minutes = _clean_int(negative_balance_limit_minutes_raw)
    weekdays_only = _clean_bool(
        _value_with_default(task_args, policy_defaults, "weekdays_only", "weekdays_only", "weekdaysOnly"),
        default=False,
    )
    weekends_only = _clean_bool(
        _value_with_default(task_args, policy_defaults, "weekends_only", "weekends_only", "weekendsOnly"),
        default=False,
    )
    night_window_enabled_raw = _value_with_default(
        task_args,
        policy_defaults,
        "night_window_enabled",
        "night_window_enabled",
        "nightWindowEnabled",
    )
    night_window_enabled = _clean_bool(
        night_window_enabled_raw,
        default=False,
    )
    night_window_start_raw = _first_value(task_args, "night_window_start", "nightWindowStart")
    if night_window_start_raw is None and night_window_enabled:
        night_window_start_raw = policy_defaults.get("night_window_start")
    night_window_start = _clean_time(night_window_start_raw)
    night_window_end_raw = _first_value(task_args, "night_window_end", "nightWindowEnd")
    if night_window_end_raw is None and night_window_enabled:
        night_window_end_raw = policy_defaults.get("night_window_end")
    night_window_end = _clean_time(night_window_end_raw)
    work_location_ids, work_location_error = _clean_work_location_ids_with_defaults(
        task_args,
        policy_defaults,
    )
    max_total_hours_window_weeks_raw = _value_with_default(
        task_args,
        policy_defaults,
        "max_total_hours_window_weeks",
        "max_total_hours_window_weeks",
        "maxTotalHoursWindowWeeks",
    )
    max_total_hours_window_weeks = _clean_int(max_total_hours_window_weeks_raw)
    max_total_hours_per_window_raw = _value_with_default(
        task_args,
        policy_defaults,
        "max_total_hours_per_window",
        "max_total_hours_per_window",
        "maxTotalHoursPerWindow",
    )
    max_total_hours_per_window = _clean_decimal(max_total_hours_per_window_raw)
    night_premium_shift_worker_exclusion_enabled = _clean_bool(
        _value_with_default(
            task_args,
            policy_defaults,
            "night_premium_shift_worker_exclusion_enabled",
            "night_premium_shift_worker_exclusion_enabled",
            "nightPremiumShiftWorkerExclusionEnabled",
        ),
        default=False,
    )
    rest_day_compensation_mode_raw = _value_with_default(
        task_args,
        policy_defaults,
        "rest_day_compensation_mode",
        "rest_day_compensation_mode",
        "restDayCompensationMode",
    )
    rest_day_compensation_mode = _clean_enum(
        rest_day_compensation_mode_raw,
        REST_DAY_COMPENSATION_MODES,
    )
    max_consecutive_rest_day_work_days_raw = _value_with_default(
        task_args,
        policy_defaults,
        "max_consecutive_rest_day_work_days",
        "max_consecutive_rest_day_work_days",
        "maxConsecutiveRestDayWorkDays",
    )
    max_consecutive_rest_day_work_days = _clean_int(max_consecutive_rest_day_work_days_raw)
    day_worker_rest_day_sequence_exemption_enabled = _clean_bool(
        _value_with_default(
            task_args,
            policy_defaults,
            "day_worker_rest_day_sequence_exemption_enabled",
            "day_worker_rest_day_sequence_exemption_enabled",
            "dayWorkerRestDaySequenceExemptionEnabled",
        ),
        default=False,
    )

    if not name:
        return error_result("overtime_policy_name_required")
    if enabled is None:
        return error_result("overtime_policy_enabled_required")
    if not trigger_unit:
        return error_result("invalid_trigger_unit")
    if not threshold_behavior:
        return error_result("invalid_threshold_behavior")
    if not threshold_source:
        return error_result("invalid_threshold_source")
    if calculation_mode_raw is not None and not calculation_mode:
        return error_result("invalid_calculation_mode")
    calculation_mode = calculation_mode or "POSITIVE_OVERTIME_ONLY"
    if rest_day_compensation_mode_raw is not None and not rest_day_compensation_mode:
        return error_result("invalid_rest_day_compensation_mode")
    rest_day_compensation_mode = rest_day_compensation_mode or "NONE"
    if weekdays_only and weekends_only:
        return error_result("policy_cannot_be_both_weekdays_only_and_weekends_only")
    if negative_balance_limit_minutes_raw is not None and negative_balance_limit_minutes is None:
        return error_result("invalid_negative_balance_limit_minutes")
    if negative_balance_limit_minutes is not None and negative_balance_limit_minutes < 0:
        return error_result("negative_balance_limit_minutes_must_be_non_negative")
    if calculation_mode == "FLEXIBLE_TIME_BALANCE" and negative_balance_limit_minutes is None:
        return error_result("negative_balance_limit_minutes_required_for_flexible_time_balance")
    if calculation_mode != "FLEXIBLE_TIME_BALANCE" and negative_balance_limit_minutes is not None:
        return error_result("negative_balance_limit_minutes_only_allowed_for_flexible_time_balance")
    if threshold_source == "SHIFT_TARGET" and threshold_hours is not None:
        return error_result("threshold_hours_must_be_null_when_threshold_source_is_shift_target")
    if threshold_source == "FIXED" and threshold_hours is None:
        return error_result("threshold_hours_required_when_threshold_source_is_fixed")
    if threshold_hours is not None and threshold_hours < 0:
        return error_result("threshold_hours_must_be_non_negative")
    if trigger_unit == "WEEKLY" and threshold_source != "FIXED":
        return error_result("weekly_policies_must_use_fixed_threshold")
    if night_window_enabled and (night_window_start is None or night_window_end is None):
        return error_result("night_window_start_and_end_required_when_night_window_is_enabled")
    if not night_window_enabled and (night_window_start is not None or night_window_end is not None):
        return error_result("night_window_times_must_be_null_when_night_window_is_disabled")
    if work_location_error:
        return error_result(work_location_error)
    if max_total_hours_window_weeks_raw is not None and max_total_hours_window_weeks is None:
        return error_result("invalid_max_total_hours_window_weeks")
    if max_total_hours_window_weeks is not None and max_total_hours_window_weeks <= 0:
        return error_result("max_total_hours_window_weeks_must_be_positive")
    if max_total_hours_per_window_raw is not None and max_total_hours_per_window is None:
        return error_result("invalid_max_total_hours_per_window")
    if max_total_hours_per_window is not None and max_total_hours_per_window < 0:
        return error_result("max_total_hours_per_window_must_be_non_negative")
    if (max_total_hours_window_weeks is None) != (max_total_hours_per_window is None):
        return error_result("max_total_hours_window_weeks_and_max_total_hours_per_window_must_be_provided_together")
    if night_premium_shift_worker_exclusion_enabled is None:
        return error_result("invalid_night_premium_shift_worker_exclusion_enabled")
    if max_consecutive_rest_day_work_days_raw is not None and max_consecutive_rest_day_work_days is None:
        return error_result("invalid_max_consecutive_rest_day_work_days")
    if max_consecutive_rest_day_work_days is not None and max_consecutive_rest_day_work_days <= 0:
        return error_result("max_consecutive_rest_day_work_days_must_be_positive")
    if day_worker_rest_day_sequence_exemption_enabled:
        return error_result("day_worker_rest_day_sequence_exemption_requires_ems_worker_category_support")

    caps: dict[str, int | float | None] = {}
    for field, aliases in CAP_FIELDS.items():
        raw_value = _value_with_default(task_args, policy_defaults, field, *aliases)
        value = _clean_decimal(raw_value)
        if raw_value is not None and value is None:
            return error_result(f"invalid_{field}")
        if value is not None and value < 0:
            return error_result(f"{field}_must_be_non_negative")
        caps[field] = _normalize_number(value)

    payload = {
        "name": name,
        "description": description,
        "enabled": enabled,
        "trigger_unit": trigger_unit,
        "threshold_behavior": threshold_behavior,
        "threshold_source": threshold_source,
        "calculation_mode": calculation_mode,
        "negative_balance_limit_minutes": negative_balance_limit_minutes,
        "threshold_hours": _normalize_number(threshold_hours),
        "weekdays_only": weekdays_only,
        "weekends_only": weekends_only,
        "max_daily_overtime_hours": caps["max_daily_overtime_hours"],
        "max_daily_overtime_percent_of_normal_hours": caps["max_daily_overtime_percent_of_normal_hours"],
        "max_total_daily_hours": caps["max_total_daily_hours"],
        "max_monthly_overtime_hours": caps["max_monthly_overtime_hours"],
        "max_yearly_overtime_hours": caps["max_yearly_overtime_hours"],
        "max_extended_yearly_overtime_hours": caps["max_extended_yearly_overtime_hours"],
        "night_window_enabled": night_window_enabled,
        "night_window_start": night_window_start if night_window_enabled else None,
        "night_window_end": night_window_end if night_window_enabled else None,
        "work_location_ids": work_location_ids,
        "max_total_hours_window_weeks": max_total_hours_window_weeks,
        "max_total_hours_per_window": _normalize_number(max_total_hours_per_window),
        "night_premium_shift_worker_exclusion_enabled": night_premium_shift_worker_exclusion_enabled,
        "rest_day_compensation_mode": rest_day_compensation_mode,
        "max_consecutive_rest_day_work_days": max_consecutive_rest_day_work_days,
        "day_worker_rest_day_sequence_exemption_enabled": day_worker_rest_day_sequence_exemption_enabled,
    }

    return ok_result({
        "content": payload,
        "action": ACTION_NAME,
    })
