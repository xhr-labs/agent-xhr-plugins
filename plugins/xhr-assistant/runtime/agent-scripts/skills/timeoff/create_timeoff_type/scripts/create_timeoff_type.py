from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.shared.task_args_cli import CLI_BOOL, CLI_STR
from src.shared.skill_wrapper import run_skill_entry


if __name__ == "__main__":
    run_skill_entry(
        "src.application.timeoff.create_timeoff_type",
        [
            {"flag": "--name", "dest": "name", "type": CLI_STR},
            {"flag": "--code", "dest": "code", "type": CLI_STR},
            {"flag": "--color", "dest": "color", "type": CLI_STR},
            {"flag": "--is-paid", "dest": "is_paid", "type": CLI_BOOL},
            {"flag": "--requires-attachment", "dest": "requires_attachment", "type": CLI_BOOL},
            {"flag": "--requires-reason", "dest": "requires_reason", "type": CLI_BOOL},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
