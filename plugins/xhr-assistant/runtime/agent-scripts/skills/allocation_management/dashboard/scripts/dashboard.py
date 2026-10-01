from src.shared.task_args_cli import CLI_STR
from src.shared.skill_wrapper import run_skill_entry


ARGUMENT_SPECS = [
    {"flag": "--month", "dest": "month", "type": CLI_STR, "required": True},
    {"flag": "--timeline", "dest": "timeline", "type": CLI_STR},
    {"flag": "--from-month", "dest": "fromMonth", "type": CLI_STR},
    {"flag": "--to-month", "dest": "toMonth", "type": CLI_STR},
    {"flag": "--department-id", "dest": "departmentId", "type": CLI_STR},
    {"flag": "--employee-type-id", "dest": "employeeTypeId", "type": CLI_STR},
    {"flag": "--work-location-id", "dest": "workLocationId", "type": CLI_STR},
    {"flag": "--job-title-id", "dest": "jobTitleId", "type": CLI_STR},
    {"flag": "--source-line-key", "dest": "sourceLineKey", "type": CLI_STR},
    {"flag": "--allocated-line-key", "dest": "allocatedLineKey", "type": CLI_STR},
    {"flag": "--product-line-id", "dest": "productLineId", "type": CLI_STR},
    {"flag": "--project-id", "dest": "projectId", "type": CLI_STR},
    {"flag": "--employee-id", "dest": "employeeId", "type": CLI_STR},
]


if __name__ == "__main__":
    run_skill_entry(
        "src.application.allocation_management.dashboard",
        ARGUMENT_SPECS,
        injected_task_args=globals().get("TASK_ARGS"),
    )
