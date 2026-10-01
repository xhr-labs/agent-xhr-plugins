from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.shared.task_args_cli import CLI_INT
from src.shared.skill_wrapper import run_skill_entry


if __name__ == "__main__":
    run_skill_entry(
        "src.application.workbench.show_my_highest_priority_task",
        [
            {"flag": "--page-number", "dest": "page_number", "type": CLI_INT},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
