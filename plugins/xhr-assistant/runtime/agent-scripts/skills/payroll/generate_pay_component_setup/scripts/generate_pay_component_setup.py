from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.shared.task_args_cli import CLI_BOOL, CLI_STR
from src.shared.skill_wrapper import run_skill_entry


if __name__ == "__main__":
    run_skill_entry(
        "src.application.payroll.generate_pay_component_setup",
        [
            {"flag": "--name", "dest": "name", "type": CLI_STR},
            {"flag": "--content", "dest": "content", "type": CLI_STR},
            {"flag": "--assistant-message", "dest": "assistant_message", "type": CLI_STR},
            {"flag": "--work-location-id", "dest": "work_location_id", "type": CLI_STR},
            {"flag": "--work-location-name", "dest": "work_location_name", "type": CLI_STR},
            {"flag": "--type", "dest": "type", "type": CLI_STR},
            {"flag": "--description", "dest": "description", "type": CLI_STR},
            {"flag": "--calculation-method", "dest": "calculation_method", "type": CLI_STR},
            {"flag": "--default-amount", "dest": "default_amount", "type": CLI_STR},
            {"flag": "--currency", "dest": "currency", "type": CLI_STR},
            {"flag": "--formula", "dest": "formula", "type": CLI_STR},
            {"flag": "--formula-variable-label", "dest": "formula_variable_label", "type": CLI_STR},
            {"flag": "--formula-percent", "dest": "formula_percent", "type": CLI_STR},
            {"flag": "--formula-multiplier", "dest": "formula_multiplier", "type": CLI_STR},
            {"flag": "--apply-tax", "dest": "apply_tax", "type": CLI_BOOL},
            {"flag": "--tax-treatment", "dest": "tax_treatment", "type": CLI_STR},
            {"flag": "--proration-enabled", "dest": "proration_enabled", "type": CLI_BOOL},
            {
                "flag": "--proration-rule-override-id",
                "dest": "proration_rule_override_id",
                "type": CLI_STR,
            },
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
