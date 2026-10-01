from src.shared.task_args_cli import CLI_INT
from src.shared.skill_wrapper import run_skill_entry


if __name__ == "__main__":
    run_skill_entry(
        "src.application.calendar.get_public_holidays",
        [
            {"flag": "--year", "dest": "year", "type": CLI_INT},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
