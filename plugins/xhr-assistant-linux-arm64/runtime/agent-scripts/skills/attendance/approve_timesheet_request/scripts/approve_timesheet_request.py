from src.shared.task_args_cli import CLI_BOOL, CLI_STR
from src.shared.skill_wrapper import run_skill_entry


if __name__ == "__main__":
    run_skill_entry(
        "src.application.attendance.approve_timesheet_request",
        [
            {"flag": "--timesheet-request-id", "dest": "timesheet_request_id", "type": CLI_STR},
            {"flag": "--note", "dest": "note", "type": CLI_STR},
            {"flag": "--mine", "dest": "mine", "type": CLI_BOOL},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
