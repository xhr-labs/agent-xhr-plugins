from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.shared.task_args_cli import CLI_APPEND_STR, CLI_BOOL, CLI_STR
from src.shared.skill_wrapper import run_skill_entry


if __name__ == "__main__":
    run_skill_entry(
        "src.application.attendance.generate_overtime_policy",
        [
            {"flag": "--name", "dest": "name", "type": CLI_STR},
            {"flag": "--description", "dest": "description", "type": CLI_STR},
            {"flag": "--jurisdiction", "dest": "jurisdiction", "type": CLI_STR},
            {"flag": "--enabled", "dest": "enabled", "type": CLI_BOOL},
            {"flag": "--trigger-unit", "dest": "trigger_unit", "type": CLI_STR},
            {"flag": "--threshold-behavior", "dest": "threshold_behavior", "type": CLI_STR},
            {"flag": "--threshold-source", "dest": "threshold_source", "type": CLI_STR},
            {"flag": "--threshold-hours", "dest": "threshold_hours", "type": CLI_STR},
            {"flag": "--calculation-mode", "dest": "calculation_mode", "type": CLI_STR},
            {"flag": "--negative-balance-limit-minutes", "dest": "negative_balance_limit_minutes", "type": CLI_STR},
            {"flag": "--weekdays-only", "dest": "weekdays_only", "type": CLI_BOOL},
            {"flag": "--weekends-only", "dest": "weekends_only", "type": CLI_BOOL},
            {"flag": "--max-daily-overtime-hours", "dest": "max_daily_overtime_hours", "type": CLI_STR},
            {"flag": "--max-daily-overtime-percent-of-normal-hours", "dest": "max_daily_overtime_percent_of_normal_hours", "type": CLI_STR},
            {"flag": "--max-total-daily-hours", "dest": "max_total_daily_hours", "type": CLI_STR},
            {"flag": "--max-monthly-overtime-hours", "dest": "max_monthly_overtime_hours", "type": CLI_STR},
            {"flag": "--max-yearly-overtime-hours", "dest": "max_yearly_overtime_hours", "type": CLI_STR},
            {"flag": "--max-extended-yearly-overtime-hours", "dest": "max_extended_yearly_overtime_hours", "type": CLI_STR},
            {"flag": "--work-location-ids", "dest": "work_location_ids", "type": CLI_APPEND_STR},
            {"flag": "--max-total-hours-window-weeks", "dest": "max_total_hours_window_weeks", "type": CLI_STR},
            {"flag": "--max-total-hours-per-window", "dest": "max_total_hours_per_window", "type": CLI_STR},
            {"flag": "--night-window-enabled", "dest": "night_window_enabled", "type": CLI_BOOL},
            {"flag": "--night-window-start", "dest": "night_window_start", "type": CLI_STR},
            {"flag": "--night-window-end", "dest": "night_window_end", "type": CLI_STR},
            {
                "flag": "--night-premium-shift-worker-exclusion-enabled",
                "dest": "night_premium_shift_worker_exclusion_enabled",
                "type": CLI_BOOL,
            },
            {"flag": "--rest-day-compensation-mode", "dest": "rest_day_compensation_mode", "type": CLI_STR},
            {
                "flag": "--max-consecutive-rest-day-work-days",
                "dest": "max_consecutive_rest_day_work_days",
                "type": CLI_STR,
            },
            {
                "flag": "--day-worker-rest-day-sequence-exemption-enabled",
                "dest": "day_worker_rest_day_sequence_exemption_enabled",
                "type": CLI_BOOL,
            },
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
