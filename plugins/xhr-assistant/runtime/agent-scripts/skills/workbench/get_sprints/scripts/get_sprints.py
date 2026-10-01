from src.shared.skill_wrapper import run_skill_entry
from src.shared.task_args_cli import CLI_BOOL, CLI_STR


if __name__ == "__main__":
    run_skill_entry(
        "src.application.workbench.get_sprints",
        [
            {"flag": "--project-id", "dest": "project_id", "type": CLI_STR, "required": True},
            {"flag": "--include-metrics", "dest": "include_metrics", "type": CLI_BOOL},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
