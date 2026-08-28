from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.shared.skill_wrapper import run_skill_entry
from src.shared.task_args_cli import CLI_STR


if __name__ == "__main__":
    run_skill_entry(
        "src.application.documents.search_company_document",
        [
            {"flag": "--query", "dest": "query", "type": CLI_STR, "required": True},
            {"flag": "--source", "dest": "source", "type": CLI_STR, "default": "wiki"},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
