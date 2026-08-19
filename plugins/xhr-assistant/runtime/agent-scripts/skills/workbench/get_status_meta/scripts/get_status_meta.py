from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.shared.task_args_cli import CLI_APPEND_STR
from src.shared.skill_wrapper import run_skill_entry


if __name__ == "__main__":
    run_skill_entry(
        "src.application.workbench.get_status_meta",
        [
            {"flag": "--status-type", "dest": "status_type", "type": CLI_APPEND_STR},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
