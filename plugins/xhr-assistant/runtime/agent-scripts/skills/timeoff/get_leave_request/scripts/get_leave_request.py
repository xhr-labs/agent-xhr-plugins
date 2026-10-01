from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.shared.task_args_cli import CLI_BOOL, CLI_INT, CLI_STR
from src.shared.skill_wrapper import run_skill_entry


if __name__ == "__main__":
    run_skill_entry(
        "src.application.timeoff.get_leave_request",
        [
            {"flag": "--status", "dest": "status", "type": CLI_STR},
            {"flag": "--employee-id", "dest": "employee_id", "type": CLI_STR},
            {"flag": "--mine", "dest": "mine", "type": CLI_BOOL},
            {"flag": "--from-date", "dest": "from_date", "type": CLI_STR},
            {"flag": "--to-date", "dest": "to_date", "type": CLI_STR},
            {"flag": "--page", "dest": "page", "type": CLI_INT},
            {"flag": "--size", "dest": "size", "type": CLI_INT},
            {"flag": "--recursive", "dest": "recursive", "type": CLI_BOOL},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
