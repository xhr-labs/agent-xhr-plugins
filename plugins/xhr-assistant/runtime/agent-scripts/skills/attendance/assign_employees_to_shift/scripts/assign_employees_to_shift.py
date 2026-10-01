from src.shared.task_args_cli import CLI_APPEND_STR, CLI_STR
from src.shared.skill_wrapper import run_skill_entry


if __name__ == "__main__":
    run_skill_entry(
        "src.application.attendance.assign_employees_to_shift",
        [
            {"flag": "--shift-id", "dest": "shift_id", "type": CLI_STR},
            {"flag": "--shift-name", "dest": "shift_name", "type": CLI_STR},
            {"flag": "--employee-id", "dest": "employee_ids", "type": CLI_APPEND_STR},
            {"flag": "--employee-name", "dest": "employee_names", "type": CLI_APPEND_STR},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
