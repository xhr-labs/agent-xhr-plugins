from src.shared.task_args_cli import CLI_STR
from src.shared.skill_wrapper import run_skill_entry


if __name__ == "__main__":
    run_skill_entry(
        "src.application.access_control.update_app_permissions",
        [
            {"flag": "--app", "dest": "app", "type": CLI_STR},
            {"flag": "--block", "dest": "block", "type": CLI_STR},
            {"flag": "--operation", "dest": "operation", "type": CLI_STR},
            {"flag": "--action", "dest": "action", "type": CLI_STR},
            {"flag": "--relations", "dest": "relations", "type": CLI_STR},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
