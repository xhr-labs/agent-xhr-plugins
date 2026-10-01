from src.shared.skill_wrapper import run_skill_entry
from src.shared.task_args_cli import CLI_STR


if __name__ == "__main__":
    run_skill_entry(
        "src.application.workbench.manage_linked_tasks",
        [
            {"flag": "--task-id", "dest": "task_id", "type": CLI_STR, "required": True},
            {"flag": "--action", "dest": "action", "type": CLI_STR},
            {"flag": "--target-task-id", "dest": "target_task_id", "type": CLI_STR},
            {"flag": "--relation-type", "dest": "relation_type", "type": CLI_STR},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
