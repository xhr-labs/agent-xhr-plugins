from src.shared.skill_wrapper import run_skill_entry
from src.shared.task_args_cli import CLI_STR


if __name__ == "__main__":
    run_skill_entry(
        "src.application.workbench.update_sprint",
        [
            {"flag": "--project-id", "dest": "project_id", "type": CLI_STR, "required": True},
            {"flag": "--sprint-id", "dest": "sprint_id", "type": CLI_STR, "required": True},
            {"flag": "--sprint-name", "dest": "sprint_name", "type": CLI_STR},
            {"flag": "--goal", "dest": "goal", "type": CLI_STR},
            {"flag": "--start-date", "dest": "start_date", "type": CLI_STR},
            {"flag": "--end-date", "dest": "end_date", "type": CLI_STR},
            {"flag": "--duration", "dest": "duration", "type": CLI_STR},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
