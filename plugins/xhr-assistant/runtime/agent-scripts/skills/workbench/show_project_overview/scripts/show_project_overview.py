from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.shared.task_args_cli import CLI_BOOL, CLI_INT, CLI_STR
from src.shared.skill_wrapper import run_skill_entry


if __name__ == "__main__":
    run_skill_entry(
        "src.application.workbench.show_project_overview",
        [
            {"flag": "--page-number", "dest": "page_number", "type": CLI_INT},
            {"flag": "--page-size", "dest": "page_size", "type": CLI_INT},
            {"flag": "--recursive", "dest": "recursive", "type": CLI_BOOL},
            {"flag": "--project-name", "dest": "project_name", "type": CLI_STR},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
