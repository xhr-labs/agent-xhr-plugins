from src.shared.skill_wrapper import run_skill_entry
from src.shared.task_args_cli import CLI_BOOL, CLI_INT, CLI_STR


if __name__ == "__main__":
    run_skill_entry(
        "src.application.workbench.manage_favorite_spaces",
        [
            {"flag": "--action", "dest": "action", "type": CLI_STR},
            {"flag": "--project-id", "dest": "project_id", "type": CLI_STR},
            {"flag": "--project-name", "dest": "project_name", "type": CLI_STR},
            {"flag": "--page", "dest": "page", "type": CLI_INT},
            {"flag": "--size", "dest": "size", "type": CLI_INT},
            {"flag": "--confirmed", "dest": "confirmed", "type": CLI_BOOL},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )