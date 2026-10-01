from src.shared.task_args_cli import CLI_BOOL, CLI_STR
from src.shared.skill_wrapper import run_skill_entry


if __name__ == "__main__":
    run_skill_entry(
        "src.application.utils.resolve_date_range",
        [
            {"flag": "--expression", "dest": "expression", "type": CLI_STR},
            {"flag": "--reference-date", "dest": "referenceDate", "type": CLI_STR},
            {"flag": "--use-reference-year-for-relative", "dest": "useReferenceYearForRelative", "type": CLI_BOOL},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
