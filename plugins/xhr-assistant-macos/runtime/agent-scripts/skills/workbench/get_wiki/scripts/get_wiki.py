from src.shared.skill_wrapper import run_skill_entry
from src.shared.task_args_cli import CLI_STR


if __name__ == "__main__":
    run_skill_entry(
        "src.application.workbench.get_wiki",
        [
            {"flag": "--page-id", "dest": "page_id", "type": CLI_STR},
            {"flag": "--page-title", "dest": "page_title", "type": CLI_STR},
            {"flag": "--project-id", "dest": "project_id", "type": CLI_STR},
            {"flag": "--project-name", "dest": "project_name", "type": CLI_STR},
            {"flag": "--scope", "dest": "scope", "type": CLI_STR},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )