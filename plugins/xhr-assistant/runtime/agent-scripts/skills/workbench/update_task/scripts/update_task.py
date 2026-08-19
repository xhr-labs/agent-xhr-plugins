from src.shared.skill_wrapper import run_skill_entry
from src.shared.task_args_cli import CLI_INT, CLI_STR


if __name__ == "__main__":
    run_skill_entry(
        "src.application.workbench.update_task",
        [
            {"flag": "--task-id", "dest": "task_id", "type": CLI_STR, "required": True},
            {"flag": "--task-name", "dest": "task_name", "type": CLI_STR},
            {"flag": "--description", "dest": "description", "type": CLI_STR},
            {"flag": "--status-id", "dest": "status_id", "type": CLI_STR},
            {"flag": "--priority", "dest": "priority", "type": CLI_STR},
            {"flag": "--assignee-id", "dest": "assignee_id", "type": CLI_STR},
            {"flag": "--assignee", "dest": "assignee", "type": CLI_STR},
            {"flag": "--reporter-id", "dest": "reporter_id", "type": CLI_STR},
            {"flag": "--reporter", "dest": "reporter", "type": CLI_STR},
            {"flag": "--start-date", "dest": "start_date", "type": CLI_STR},
            {"flag": "--due-date", "dest": "due_date", "type": CLI_STR},
            {"flag": "--project-id", "dest": "project_id", "type": CLI_STR},
            {"flag": "--sprint-id", "dest": "sprint_id", "type": CLI_STR},
            {"flag": "--story-point", "dest": "story_point", "type": CLI_INT},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
