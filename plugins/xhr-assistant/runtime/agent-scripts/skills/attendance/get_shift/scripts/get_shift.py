from src.shared.task_args_cli import CLI_BOOL, CLI_INT, CLI_STR
from src.shared.skill_wrapper import run_skill_entry


if __name__ == "__main__":
    run_skill_entry(
        "src.application.attendance.get_shift",
        [
            {"flag": "--shift-id", "dest": "shift_id", "type": CLI_STR},
            {"flag": "--shift-name", "dest": "shift_name", "type": CLI_STR},
            {"flag": "--search-keyword", "dest": "search_keyword", "type": CLI_STR},
            {"flag": "--is-active", "dest": "is_active", "type": CLI_BOOL},
            {"flag": "--page", "dest": "page", "type": CLI_INT},
            {"flag": "--size", "dest": "size", "type": CLI_INT},
            {"flag": "--sort", "dest": "sort", "type": CLI_STR},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
