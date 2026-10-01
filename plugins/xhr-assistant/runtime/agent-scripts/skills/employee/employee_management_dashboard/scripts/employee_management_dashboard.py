from src.shared.task_args_cli import CLI_STR
from src.shared.skill_wrapper import run_skill_entry


if __name__ == "__main__":
    run_skill_entry(
        "src.application.employee.employee_management_dashboard",
        [
            {"flag": "--month", "dest": "month", "type": CLI_STR, "required": True},
            {"flag": "--department-id", "dest": "departmentId", "type": CLI_STR},
            {"flag": "--employee-type-id", "dest": "employeeTypeId", "type": CLI_STR},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
