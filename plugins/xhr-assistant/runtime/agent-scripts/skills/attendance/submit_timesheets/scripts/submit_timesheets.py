from src.shared.task_args_cli import CLI_STR
from src.shared.skill_wrapper import run_skill_entry


if __name__ == "__main__":
    run_skill_entry(
        "src.application.attendance.submit_timesheets",
        [
            {"flag": "--employee-id", "dest": "employee_id", "type": CLI_STR},
            {"flag": "--entries-json", "dest": "entries_json", "type": CLI_STR},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
