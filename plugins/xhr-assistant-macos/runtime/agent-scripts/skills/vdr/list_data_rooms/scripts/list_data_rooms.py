from src.shared.task_args_cli import CLI_INT, CLI_STR
from src.shared.skill_wrapper import run_skill_entry


if __name__ == "__main__":
    run_skill_entry(
        "src.application.vdr.list_data_rooms",
        [
            {"flag": "--page", "dest": "page", "type": CLI_INT},
            {"flag": "--size", "dest": "size", "type": CLI_INT},
            {"flag": "--name", "dest": "name", "type": CLI_STR},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
