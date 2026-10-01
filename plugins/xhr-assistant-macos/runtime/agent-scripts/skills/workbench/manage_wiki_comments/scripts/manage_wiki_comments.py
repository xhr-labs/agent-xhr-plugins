from src.shared.skill_wrapper import run_skill_entry
from src.shared.task_args_cli import CLI_BOOL, CLI_INT, CLI_STR


if __name__ == "__main__":
    run_skill_entry(
        "src.application.workbench.manage_wiki_comments",
        [
            {"flag": "--action", "dest": "action", "type": CLI_STR},
            {"flag": "--project-id", "dest": "project_id", "type": CLI_STR},
            {"flag": "--project-name", "dest": "project_name", "type": CLI_STR},
            {"flag": "--page-id", "dest": "page_id", "type": CLI_STR},
            {"flag": "--page-title", "dest": "page_title", "type": CLI_STR},
            {"flag": "--thread-id", "dest": "thread_id", "type": CLI_STR},
            {"flag": "--comment-id", "dest": "comment_id", "type": CLI_STR},
            {"flag": "--content", "dest": "content", "type": CLI_STR},
            {"flag": "--selected-text", "dest": "selected_text", "type": CLI_STR},
            {"flag": "--from-pos", "dest": "from_pos", "type": CLI_INT},
            {"flag": "--to-pos", "dest": "to_pos", "type": CLI_INT},
            {"flag": "--resolved", "dest": "resolved", "type": CLI_BOOL},
            {"flag": "--scope", "dest": "scope", "type": CLI_STR},
            {"flag": "--confirmed", "dest": "confirmed", "type": CLI_BOOL},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )