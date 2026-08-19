from __future__ import annotations

import argparse
from typing import Any


def _clean_cli_scalar(value: Any) -> str:
    return str(value).strip().rstrip(".,;:")


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # pragma: no cover - exercised via script execution
        raise ValueError(message)


class _AppendValueAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        current = getattr(namespace, self.dest, None)
        if current is None:
            current = []
        current.append(values)
        setattr(namespace, self.dest, current)


class _StoreOptionalStringAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


class _StoreOptionalIntAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, int(_clean_cli_scalar(values)))


class _StoreOptionalBoolAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if isinstance(values, bool):
            setattr(namespace, self.dest, values)
            return

        lowered = _clean_cli_scalar(values).lower()
        if lowered in {"1", "true", "yes", "y", "on"}:
            setattr(namespace, self.dest, True)
            return
        if lowered in {"0", "false", "no", "n", "off"}:
            setattr(namespace, self.dest, False)
            return
        raise ValueError(f"Invalid boolean value for {option_string}: {values}")


CLI_APPEND_STR = "append-str"
CLI_STR = "str"
CLI_INT = "int"
CLI_BOOL = "bool"


def build_task_args_from_cli(argument_specs: list[dict[str, Any]]) -> dict[str, Any]:
    parser = _ArgumentParser(add_help=False)
    for spec in argument_specs:
        action_type = spec["type"]
        option = spec["flag"]
        dest = spec["dest"]
        required = bool(spec.get("required", False))

        if action_type == CLI_APPEND_STR:
            parser.add_argument(option, dest=dest, action=_AppendValueAction, required=required)
            continue
        if action_type == CLI_INT:
            parser.add_argument(option, dest=dest, action=_StoreOptionalIntAction, required=required)
            continue
        if action_type == CLI_STR:
            parser.add_argument(option, dest=dest, action=_StoreOptionalStringAction, required=required)
            continue
        if action_type == CLI_BOOL:
            parser.add_argument(option, dest=dest, action=_StoreOptionalBoolAction, required=required)
            continue
        raise ValueError(f"Unsupported CLI arg type: {action_type}")

    namespace = parser.parse_args()
    payload: dict[str, Any] = {}
    for spec in argument_specs:
        value = getattr(namespace, spec["dest"])
        if value is None:
            continue
        payload[spec["dest"]] = value
    return payload


def resolve_task_args(
    argument_specs: list[dict[str, Any]],
    injected_task_args: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    if injected_task_args is not None:
        return injected_task_args

    payload = build_task_args_from_cli(argument_specs)
    return payload or None
