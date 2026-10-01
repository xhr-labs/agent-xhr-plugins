from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.shared.task_args_cli import CLI_BOOL, CLI_INT, CLI_APPEND_STR
from src.shared.skill_wrapper import run_skill_entry


if __name__ == "__main__":
    run_skill_entry(
        "src.application.workbench.get_overdue_tasks",
        [
            {"flag": "--page-number", "dest": "page_number", "type": CLI_INT},
            {"flag": "--page-size", "dest": "page_size", "type": CLI_INT},
            {"flag": "--priority", "dest": "priority", "type": CLI_APPEND_STR},
            {"flag": "--status-id", "dest": "status_id", "type": CLI_APPEND_STR},
            {"flag": "--status-key", "dest": "status_key", "type": CLI_APPEND_STR},
            {"flag": "--status-name", "dest": "status_name", "type": CLI_APPEND_STR},
            {"flag": "--assignee-id", "dest": "assignee_id", "type": CLI_APPEND_STR},
            {"flag": "--mine", "dest": "mine", "type": CLI_BOOL},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
