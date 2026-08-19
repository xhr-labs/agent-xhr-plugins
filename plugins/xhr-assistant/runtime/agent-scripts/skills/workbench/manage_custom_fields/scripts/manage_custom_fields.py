from src.shared.skill_wrapper import run_skill_entry
from src.shared.task_args_cli import CLI_STR


if __name__ == "__main__":
    run_skill_entry(
        "src.application.workbench.manage_custom_fields",
        [
            {"flag": "--task-id", "dest": "task_id", "type": CLI_STR},
            {"flag": "--project-id", "dest": "project_id", "type": CLI_STR},
            {"flag": "--action", "dest": "action", "type": CLI_STR},
            {"flag": "--field-id", "dest": "field_id", "type": CLI_STR},
            {"flag": "--value", "dest": "value", "type": CLI_STR},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
