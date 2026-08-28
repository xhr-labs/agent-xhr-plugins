from src.shared.skill_wrapper import run_skill_entry
from src.shared.task_args_cli import CLI_BOOL, CLI_STR


if __name__ == "__main__":
    run_skill_entry(
        "src.application.workbench.update_project",
        [
            {"flag": "--project-id", "dest": "project_id", "type": CLI_STR, "required": True},
            {"flag": "--project-name", "dest": "project_name", "type": CLI_STR},
            {"flag": "--description", "dest": "description", "type": CLI_STR},
            {"flag": "--status-id", "dest": "status_id", "type": CLI_STR},
            {"flag": "--start-date", "dest": "start_date", "type": CLI_STR},
            {"flag": "--target-date", "dest": "target_date", "type": CLI_STR},
            {"flag": "--icon", "dest": "icon", "type": CLI_STR},
            {"flag": "--color", "dest": "color", "type": CLI_STR},
            {"flag": "--enable-sprint", "dest": "enable_sprint", "type": CLI_BOOL},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
