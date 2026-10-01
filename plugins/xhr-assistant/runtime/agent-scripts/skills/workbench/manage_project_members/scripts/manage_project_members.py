from src.shared.skill_wrapper import run_skill_entry
from src.shared.task_args_cli import CLI_STR


if __name__ == "__main__":
    run_skill_entry(
        "src.application.workbench.manage_project_members",
        [
            {"flag": "--project-id", "dest": "project_id", "type": CLI_STR, "required": True},
            {"flag": "--action", "dest": "action", "type": CLI_STR},
            {"flag": "--employee-id", "dest": "employee_id", "type": CLI_STR},
            {"flag": "--role", "dest": "role", "type": CLI_STR},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
