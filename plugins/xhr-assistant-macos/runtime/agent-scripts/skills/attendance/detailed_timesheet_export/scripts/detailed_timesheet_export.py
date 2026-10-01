from src.shared.task_args_cli import CLI_APPEND_STR, CLI_INT, CLI_STR
from src.shared.skill_wrapper import run_skill_entry


if __name__ == "__main__":
    run_skill_entry(
        "src.application.attendance.detailed_timesheet_export",
        [
            {"flag": "--employee-id", "dest": "employee_id", "type": CLI_STR},
            {"flag": "--start-date", "dest": "start_date", "type": CLI_STR},
            {"flag": "--end-date", "dest": "end_date", "type": CLI_STR},
            {"flag": "--statuses", "dest": "statuses", "type": CLI_APPEND_STR},
            {"flag": "--expected-minutes", "dest": "expected_minutes", "type": CLI_INT},
            {"flag": "--expected-hours", "dest": "expected_hours", "type": CLI_STR},
            {"flag": "--sort", "dest": "sort", "type": CLI_STR},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
