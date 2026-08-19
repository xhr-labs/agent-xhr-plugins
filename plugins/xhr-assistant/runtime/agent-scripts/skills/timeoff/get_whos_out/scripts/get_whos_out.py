from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.shared.task_args_cli import CLI_STR
from src.shared.skill_wrapper import run_skill_entry


if __name__ == "__main__":
    run_skill_entry(
        "src.application.timeoff.get_whos_out",
        [
            {"flag": "--from-date", "dest": "from_date", "type": CLI_STR},
            {"flag": "--to-date", "dest": "to_date", "type": CLI_STR},
            {"flag": "--department-id", "dest": "department_id", "type": CLI_STR},
            {"flag": "--employee-id", "dest": "employee_id", "type": CLI_STR},
            {"flag": "--employee-name", "dest": "employee_name", "type": CLI_STR},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
