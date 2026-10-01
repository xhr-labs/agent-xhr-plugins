from src.shared.task_args_cli import CLI_APPEND_STR, CLI_BOOL, CLI_INT, CLI_STR
from src.shared.skill_wrapper import run_skill_entry


if __name__ == "__main__":
    run_skill_entry(
        "src.application.attendance.get_timesheet_requests",
        [
            {"flag": "--employee-ids", "dest": "employee_ids", "type": CLI_APPEND_STR},
            {"flag": "--start-date", "dest": "start_date", "type": CLI_STR},
            {"flag": "--end-date", "dest": "end_date", "type": CLI_STR},
            {"flag": "--statuses", "dest": "statuses", "type": CLI_APPEND_STR},
            {"flag": "--page", "dest": "page", "type": CLI_INT},
            {"flag": "--size", "dest": "size", "type": CLI_INT},
            {"flag": "--sort", "dest": "sort", "type": CLI_STR},
            {"flag": "--mine", "dest": "mine", "type": CLI_BOOL},
            {"flag": "--recursive", "dest": "recursive", "type": CLI_BOOL},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
