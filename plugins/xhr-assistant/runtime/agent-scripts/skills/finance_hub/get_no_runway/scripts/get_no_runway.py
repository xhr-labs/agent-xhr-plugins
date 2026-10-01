from src.shared.skill_wrapper import run_skill_entry


if __name__ == "__main__":
    run_skill_entry(
        "src.application.finance_hub.get_no_runway",
        [],
        injected_task_args=globals().get("TASK_ARGS"),
    )
