from src.shared.skill_wrapper import run_skill_entry
from src.shared.task_args_cli import CLI_INT, CLI_STR


if __name__ == "__main__":
    run_skill_entry(
        "src.application.workbench.get_task_comments",
        [
            {"flag": "--task-id", "dest": "task_id", "type": CLI_STR, "required": True},
            {"flag": "--page", "dest": "page", "type": CLI_INT},
            {"flag": "--size", "dest": "size", "type": CLI_INT},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
