from src.shared.skill_wrapper import run_skill_entry
from src.shared.task_args_cli import CLI_STR


if __name__ == "__main__":
    run_skill_entry(
        "src.application.workbench.start_sprint",
        [
            {"flag": "--project-id", "dest": "project_id", "type": CLI_STR, "required": True},
            {"flag": "--sprint-id", "dest": "sprint_id", "type": CLI_STR, "required": True},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
