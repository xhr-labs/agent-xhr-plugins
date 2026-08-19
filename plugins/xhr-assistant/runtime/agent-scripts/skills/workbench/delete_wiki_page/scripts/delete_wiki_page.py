from src.shared.skill_wrapper import run_skill_entry
from src.shared.task_args_cli import CLI_BOOL, CLI_STR


if __name__ == "__main__":
    run_skill_entry(
        "src.application.workbench.delete_wiki_page",
        [
            {"flag": "--page-id", "dest": "page_id", "type": CLI_STR, "required": True},
            {"flag": "--title", "dest": "title", "type": CLI_STR},
            {"flag": "--project-id", "dest": "project_id", "type": CLI_STR},
            {"flag": "--confirmed", "dest": "confirmed", "type": CLI_BOOL},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
