from src.shared.task_args_cli import CLI_STR
from src.shared.skill_wrapper import run_skill_entry


if __name__ == "__main__":
    run_skill_entry(
        "src.application.vdr.aggregate_audit_logs",
        [
            {"flag": "--data-room", "dest": "dataRoom", "type": CLI_STR},
            {"flag": "--start-date", "dest": "startDate", "type": CLI_STR},
            {"flag": "--end-date", "dest": "endDate", "type": CLI_STR},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
