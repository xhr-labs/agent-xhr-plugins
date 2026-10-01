from src.shared.task_args_cli import CLI_BOOL, CLI_INT, CLI_STR
from src.shared.skill_wrapper import run_skill_entry


if __name__ == "__main__":
    run_skill_entry(
        "src.application.attendance.create_shift",
        [
            {"flag": "--name", "dest": "name", "type": CLI_STR},
            {"flag": "--description", "dest": "description", "type": CLI_STR},
            {"flag": "--apply-public-holiday-target-hours", "dest": "apply_public_holiday_target_hours", "type": CLI_BOOL},
            {"flag": "--target-monday-hours", "dest": "target_monday_hours", "type": CLI_INT},
            {"flag": "--target-monday-minutes", "dest": "target_monday_minutes", "type": CLI_INT},
            {"flag": "--target-tuesday-hours", "dest": "target_tuesday_hours", "type": CLI_INT},
            {"flag": "--target-tuesday-minutes", "dest": "target_tuesday_minutes", "type": CLI_INT},
            {"flag": "--target-wednesday-hours", "dest": "target_wednesday_hours", "type": CLI_INT},
            {"flag": "--target-wednesday-minutes", "dest": "target_wednesday_minutes", "type": CLI_INT},
            {"flag": "--target-thursday-hours", "dest": "target_thursday_hours", "type": CLI_INT},
            {"flag": "--target-thursday-minutes", "dest": "target_thursday_minutes", "type": CLI_INT},
            {"flag": "--target-friday-hours", "dest": "target_friday_hours", "type": CLI_INT},
            {"flag": "--target-friday-minutes", "dest": "target_friday_minutes", "type": CLI_INT},
            {"flag": "--target-saturday-hours", "dest": "target_saturday_hours", "type": CLI_INT},
            {"flag": "--target-saturday-minutes", "dest": "target_saturday_minutes", "type": CLI_INT},
            {"flag": "--target-sunday-hours", "dest": "target_sunday_hours", "type": CLI_INT},
            {"flag": "--target-sunday-minutes", "dest": "target_sunday_minutes", "type": CLI_INT},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
