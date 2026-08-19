from src.shared.skill_wrapper import run_skill_entry
from src.shared.task_args_cli import CLI_STR


if __name__ == "__main__":
    run_skill_entry(
        "src.application.workbench.move_wiki_page",
        [
            {"flag": "--page-id", "dest": "page_id", "type": CLI_STR, "required": True},
            {"flag": "--parent-id", "dest": "parent_id", "type": CLI_STR},
            {"flag": "--prev-id", "dest": "prev_id", "type": CLI_STR},
            {"flag": "--next-id", "dest": "next_id", "type": CLI_STR},
            {"flag": "--project-id", "dest": "project_id", "type": CLI_STR},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
