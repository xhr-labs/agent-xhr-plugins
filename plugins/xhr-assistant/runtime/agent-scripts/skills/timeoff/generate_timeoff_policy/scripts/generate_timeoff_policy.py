from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.shared.task_args_cli import CLI_APPEND_STR, CLI_BOOL, CLI_STR
from src.shared.skill_wrapper import run_skill_entry


if __name__ == "__main__":
    run_skill_entry(
        "src.application.timeoff.generate_timeoff_policy",
        [
            {"flag": "--jurisdiction", "dest": "jurisdiction", "type": CLI_STR},
            {"flag": "--name", "dest": "name", "type": CLI_STR},
            {"flag": "--description", "dest": "description", "type": CLI_STR},
            {"flag": "--applied-location-id", "dest": "applied_location_id", "type": CLI_STR},
            {"flag": "--applied-location-name", "dest": "applied_location_name", "type": CLI_STR},
            {"flag": "--employment-type-id", "dest": "employment_type_id", "type": CLI_STR},
            {"flag": "--employment-type-name", "dest": "employment_type_name", "type": CLI_STR},
            {"flag": "--employee-status", "dest": "employee_statuses", "type": CLI_APPEND_STR},
            {"flag": "--gender", "dest": "genders", "type": CLI_APPEND_STR},
            {"flag": "--block-probation-requests", "dest": "block_probation_requests", "type": CLI_BOOL},
            {"flag": "--length-of-service-operator", "dest": "length_of_service_operator", "type": CLI_STR},
            {"flag": "--length-of-service-value", "dest": "length_of_service_value", "type": CLI_STR},
            {"flag": "--length-of-service-days", "dest": "length_of_service_days", "type": CLI_STR},
            {"flag": "--length-of-service-months", "dest": "length_of_service_months", "type": CLI_STR},
            {"flag": "--length-of-service-unit", "dest": "length_of_service_unit", "type": CLI_STR},
            {"flag": "--time-off-type-id", "dest": "time_off_type_id", "type": CLI_STR},
            {"flag": "--time-off-type-name", "dest": "time_off_type_name", "type": CLI_STR},
            {"flag": "--annual-allowance", "dest": "annual_allowance", "type": CLI_STR},
            {"flag": "--period-allowance", "dest": "period_allowance", "type": CLI_STR},
            {"flag": "--allowance-per-month", "dest": "allowance_per_month", "type": CLI_STR},
            {"flag": "--monthly-allowance", "dest": "monthly_allowance", "type": CLI_STR},
            {"flag": "--accrual-period", "dest": "accrual_period", "type": CLI_STR},
            {"flag": "--accrual-year-starts-on", "dest": "accrual_year_starts_on", "type": CLI_STR},
            {"flag": "--accrual-timing", "dest": "accrual_timing", "type": CLI_STR},
            {"flag": "--proration-strategy", "dest": "proration_strategy", "type": CLI_STR},
            {"flag": "--effective-from", "dest": "effective_from", "type": CLI_STR},
            {"flag": "--effective-to", "dest": "effective_to", "type": CLI_STR},
            {"flag": "--retroactive-recalculation", "dest": "retroactive_recalculation", "type": CLI_BOOL},
            {"flag": "--retroactive-enabled", "dest": "retroactive_recalculation", "type": CLI_BOOL},
            {"flag": "--retroactive-effective-from", "dest": "retroactive_effective_from", "type": CLI_STR},
            {"flag": "--recalculate-from", "dest": "retroactive_effective_from", "type": CLI_STR},
            {"flag": "--reset-manual-balance-adjustments", "dest": "reset_manual_balance_adjustments", "type": CLI_BOOL},
            {"flag": "--reset-applied-policy-accruals", "dest": "reset_applied_policy_accruals", "type": CLI_BOOL},
            {"flag": "--carryover-enabled", "dest": "carryover_enabled", "type": CLI_BOOL},
            {"flag": "--carryover-max-days", "dest": "carryover_max_days", "type": CLI_STR},
            {"flag": "--carryover-expiry-value", "dest": "carryover_expiry_value", "type": CLI_STR},
            {"flag": "--carryover-expiry-unit", "dest": "carryover_expiry_unit", "type": CLI_STR},
            {"flag": "--advance-leave-enabled", "dest": "advance_leave_enabled", "type": CLI_BOOL},
            {"flag": "--advance-leave-limit-days", "dest": "advance_leave_limit_days", "type": CLI_STR},
            {"flag": "--negative-balance-limit-days", "dest": "advance_leave_limit_days", "type": CLI_STR},
            {"flag": "--seniority-bonus-enabled", "dest": "seniority_bonus_enabled", "type": CLI_BOOL},
            {"flag": "--seniority-bonus-proration", "dest": "seniority_bonus_proration", "type": CLI_STR},
            {"flag": "--seniority-bonus-rounding-rule", "dest": "seniority_bonus_rounding_rule", "type": CLI_STR},
            {"flag": "--seniority-bonus-step", "dest": "seniority_bonus_steps", "type": CLI_APPEND_STR},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
