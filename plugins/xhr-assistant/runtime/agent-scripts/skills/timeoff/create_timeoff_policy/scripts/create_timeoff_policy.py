from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.shared.task_args_cli import CLI_FLOAT, CLI_STR
from src.shared.skill_wrapper import run_skill_entry


if __name__ == "__main__":
    run_skill_entry(
        "src.application.timeoff.create_timeoff_policy",
        [
            {"flag": "--name", "dest": "name", "type": CLI_STR},
            {"flag": "--time-off-type-id", "dest": "time_off_type_id", "type": CLI_STR},
            {"flag": "--allowance", "dest": "allowance", "type": CLI_FLOAT},
            {"flag": "--accrual-frequency", "dest": "accrual_frequency", "type": CLI_STR},
            {"flag": "--accrual-period", "dest": "accrual_period", "type": CLI_STR},
            {"flag": "--applied-location-id", "dest": "applied_location_id", "type": CLI_STR},
            {"flag": "--effective-from", "dest": "effective_from", "type": CLI_STR},
            {"flag": "--description", "dest": "description", "type": CLI_STR},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
