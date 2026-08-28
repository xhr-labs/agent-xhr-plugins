from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.shared.task_args_cli import CLI_STR
from src.shared.skill_wrapper import run_skill_entry


if __name__ == "__main__":
    run_skill_entry(
        "src.application.workbench.create_task",
        [
            {"flag": "--task-name", "dest": "task_name", "type": CLI_STR},
            {"flag": "--project-id", "dest": "project_id", "type": CLI_STR},
            {"flag": "--project-name", "dest": "project_name", "type": CLI_STR},
            {"flag": "--status", "dest": "status", "type": CLI_STR},
            {"flag": "--priority", "dest": "priority", "type": CLI_STR},
            {"flag": "--assignee-id", "dest": "assignee_id", "type": CLI_STR},
            {"flag": "--assignee", "dest": "assignee", "type": CLI_STR},
            {"flag": "--start-date", "dest": "start_date", "type": CLI_STR},
            {"flag": "--end-date", "dest": "end_date", "type": CLI_STR},
            {"flag": "--description", "dest": "description", "type": CLI_STR},
            {"flag": "--confirmed", "dest": "confirmed", "type": CLI_STR},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
