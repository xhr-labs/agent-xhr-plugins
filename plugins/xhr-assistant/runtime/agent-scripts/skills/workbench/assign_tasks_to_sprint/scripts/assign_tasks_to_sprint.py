from src.shared.skill_wrapper import run_skill_entry
from src.shared.task_args_cli import CLI_APPEND_STR, CLI_STR


if __name__ == "__main__":
    run_skill_entry(
        "src.application.workbench.assign_tasks_to_sprint",
        [
            {"flag": "--project-id", "dest": "project_id", "type": CLI_STR, "required": True},
            {"flag": "--sprint-id", "dest": "sprint_id", "type": CLI_STR, "required": True},
            {"flag": "--task-id", "dest": "task_ids", "type": CLI_APPEND_STR, "required": True},
            {"flag": "--action", "dest": "action", "type": CLI_STR},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
