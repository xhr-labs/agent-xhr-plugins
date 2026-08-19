from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.shared.task_args_cli import CLI_BOOL, CLI_STR
from src.shared.skill_wrapper import run_skill_entry


if __name__ == "__main__":
    run_skill_entry(
        "src.application.workbench.create_project",
        [
            {"flag": "--project-name", "dest": "project_name", "type": CLI_STR},
            {"flag": "--description", "dest": "description", "type": CLI_STR},
            {"flag": "--start-date", "dest": "start_date", "type": CLI_STR},
            {"flag": "--due-date", "dest": "due_date", "type": CLI_STR},
            {"flag": "--status", "dest": "status", "type": CLI_STR},
            {"flag": "--status-id", "dest": "status_id", "type": CLI_STR},
            {"flag": "--enable-sprint", "dest": "enable_sprint", "type": CLI_BOOL},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
