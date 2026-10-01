from src.shared.skill_wrapper import run_skill_entry
from src.shared.task_args_cli import CLI_INT, CLI_STR


if __name__ == "__main__":
    run_skill_entry(
        "src.application.attendance.attendance_reports",
        [
            {"flag": "--status", "dest": "status", "type": CLI_STR},
            {"flag": "--mode", "dest": "mode", "type": CLI_STR},
            {"flag": "--month", "dest": "month", "type": CLI_STR},
            {"flag": "--year", "dest": "year", "type": CLI_INT},
            {"flag": "--start-date", "dest": "startDate", "type": CLI_STR},
            {"flag": "--end-date", "dest": "endDate", "type": CLI_STR},
            {"flag": "--department-id", "dest": "departmentId", "type": CLI_STR},
            {"flag": "--search-name", "dest": "searchName", "type": CLI_STR},
            {"flag": "--employee-id", "dest": "employeeId", "type": CLI_STR},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
