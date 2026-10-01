from src.shared.skill_wrapper import run_skill_entry
from src.shared.task_args_cli import CLI_STR


if __name__ == "__main__":
    run_skill_entry(
        "src.application.workbench.log_task_time",
        [
            {"flag": "--task-id", "dest": "task_id", "type": CLI_STR, "required": True},
            {"flag": "--duration", "dest": "duration", "type": CLI_STR, "required": True},
            {"flag": "--work-date", "dest": "work_date", "type": CLI_STR},
            {"flag": "--notes", "dest": "notes", "type": CLI_STR},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
