from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.shared.task_args_cli import CLI_FLOAT, CLI_STR
from src.shared.skill_wrapper import run_skill_entry


if __name__ == "__main__":
    run_skill_entry(
        "src.application.exm.submit_expense",
        [
            {"flag": "--name", "dest": "name", "type": CLI_STR},
            {"flag": "--expense-date", "dest": "expense_date", "type": CLI_STR},
            {"flag": "--category-id", "dest": "category_id", "type": CLI_STR},
            {"flag": "--amount", "dest": "amount", "type": CLI_FLOAT},
            {"flag": "--currency", "dest": "currency", "type": CLI_STR},
            {"flag": "--exchange-rate", "dest": "exchange_rate", "type": CLI_FLOAT},
            {"flag": "--merchant", "dest": "merchant", "type": CLI_STR},
            {"flag": "--description", "dest": "description", "type": CLI_STR},
            {"flag": "--documents-json", "dest": "documents_json", "type": CLI_STR},
            {"flag": "--items-json", "dest": "items_json", "type": CLI_STR},
            {"flag": "--idempotency-key", "dest": "idempotency_key", "type": CLI_STR},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
