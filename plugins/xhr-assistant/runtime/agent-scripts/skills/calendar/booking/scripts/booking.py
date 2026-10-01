from src.shared.task_args_cli import CLI_BOOL, CLI_INT, CLI_STR
from src.shared.skill_wrapper import run_skill_entry


if __name__ == "__main__":
    run_skill_entry(
        "src.application.calendar.booking",
        [
            {"flag": "--colleague-id", "dest": "colleagueId", "type": CLI_STR},
            {"flag": "--colleague-name", "dest": "colleagueName", "type": CLI_STR},
            {"flag": "--duration-minutes", "dest": "durationMinutes", "type": CLI_INT},
            {"flag": "--range-start", "dest": "rangeStart", "type": CLI_STR},
            {"flag": "--range-end", "dest": "rangeEnd", "type": CLI_STR},
            {"flag": "--slot-start", "dest": "slotStart", "type": CLI_STR},
            {"flag": "--slot-end", "dest": "slotEnd", "type": CLI_STR},
            {"flag": "--confirm", "dest": "confirm", "type": CLI_BOOL},
            {"flag": "--notes", "dest": "notes", "type": CLI_STR},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
