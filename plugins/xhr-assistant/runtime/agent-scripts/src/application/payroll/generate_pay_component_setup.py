from __future__ import annotations

from decimal import Decimal, InvalidOperation
import json
import re
from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text
from src.shared.result import error_result, ok_result


ACTION_NAME = "payroll_pay_component_setup"
CLIENT_CONTEXT_DATA_HEADER = "x-agent-client-context-data"
CALCULATION_METHODS = {"FIXED_AMOUNT", "MANUAL_INPUT", "FORMULA"}
PAY_COMPONENT_TYPES = {"EARNINGS", "DEDUCTION"}
TAX_TREATMENTS = {"TAXABLE", "NON_TAXABLE", "PRE_TAX", "POST_TAX"}
FORMULA_TOKEN_PATTERN = re.compile(r"\$\{([^{}]+)\}")
FORMULA_ALLOWED_PATTERN = re.compile(r"^[0-9+\-*/().,\s]+$")
LOCATION_WORDS = {
    "ae",
    "uae",
    "united",
    "arab",
    "emirates",
    "emirate",
    "vn",
    "vietnam",
    "viet",
    "nam",
}
FORMULA_LABEL_PREFIXES = {
    "salary",
    "allowance",
    "deduction",
    "earnings",
    "earning",
    "pc",
    "pay",
    "component",
    "compensation",
    "type",
}
CURRENCY_PATTERN = re.compile(r"\b[A-Z]{3}\b")


def _first_value(task_args: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in task_args and task_args[key] is not None:
            return task_args[key]
    return None


def _clean_enum(value: Any, supported: set[str]) -> str | None:
    text = clean_text(value)
    if not text:
        return None
    normalized = text.upper()
    return normalized if normalized in supported else None


def _clean_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and value in {0, 1}:
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "y", "on"}:
            return True
        if normalized in {"0", "false", "no", "n", "off"}:
            return False
    return None


def _clean_decimal(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, str):
        trimmed = value.strip()
        if not trimmed:
            return None
        try:
            return Decimal(trimmed)
        except InvalidOperation:
            return None
    return None


def _normalize_number(value: Decimal | None) -> int | float | None:
    if value is None:
        return None
    return int(value) if value == value.to_integral_value() else float(value)


def _formula_decimal_text(value: Decimal) -> str:
    normalized = value.normalize()
    text = format(normalized, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _client_context_data(context: RequestContext) -> dict[str, Any]:
    request_headers = context.request_headers if isinstance(context.request_headers, dict) else {}
    raw = request_headers.get(CLIENT_CONTEXT_DATA_HEADER)
    if not isinstance(raw, str) or not raw.strip():
        return {}
    try:
        parsed = json.loads(raw)
    except Exception:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _current_pay_component(context_data: dict[str, Any]) -> dict[str, Any]:
    current = context_data.get("current_pay_component")
    return current if isinstance(current, dict) else {}


def _work_locations(context_data: dict[str, Any]) -> list[dict[str, Any]]:
    raw = context_data.get("payroll_work_locations")
    if not isinstance(raw, list):
        return []
    return [location for location in raw if isinstance(location, dict)]


def _context_value(current: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = current.get(key)
        if value is not None:
            return value
    return None


def _location_value(location: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = location.get(key)
        if value is not None:
            return value
    return None


def _location_display_name(location: dict[str, Any]) -> str | None:
    return clean_text(
        _location_value(
            location,
            "name",
            "work_location_name",
            "workLocationName",
            "country_name",
            "countryName",
            "city_name",
            "cityName",
        )
    )


def _location_required_error_result(work_locations: list[dict[str, Any]]) -> dict[str, Any]:
    labels = [
        label
        for label in (_location_display_name(location) for location in work_locations)
        if label
    ]
    if labels:
        user_message = "Location is required. Ask the user to choose one of these locations: " + ", ".join(labels) + "."
    else:
        user_message = "Location is required. Ask the user which work location to use."
    return {
        "ok": False,
        "error": "pay_component_work_location_required",
        "data": {
            "user_message": user_message,
            "locations": [
                {
                    "id": clean_text(_location_value(location, "id")),
                    "name": _location_display_name(location),
                }
                for location in work_locations
            ],
        },
    }


def _match_work_location_by_id(
    work_locations: list[dict[str, Any]],
    location_id: str | None,
) -> dict[str, Any] | None:
    if not location_id:
        return None
    for location in work_locations:
        if (
            clean_text(_location_value(location, "id", "work_location_id"))
            == location_id
        ):
            return location
    return None


def _match_work_location_by_name(
    work_locations: list[dict[str, Any]],
    location_name: str | None,
) -> dict[str, Any] | None:
    if not location_name:
        return None
    normalized_name = location_name.casefold()
    matches = []
    for location in work_locations:
        candidates = {
            clean_text(_location_value(location, "name", "work_location_name")),
            clean_text(_location_value(location, "country_name", "countryName")),
            clean_text(_location_value(location, "city_name", "cityName")),
        }
        normalized_candidates = {
            candidate.casefold() for candidate in candidates if candidate
        }
        if normalized_name in normalized_candidates:
            matches.append(location)
    return matches[0] if len(matches) == 1 else None


def _location_search_terms(location: dict[str, Any]) -> set[str]:
    terms: set[str] = set()
    for key, value in location.items():
        if not isinstance(value, str):
            continue
        normalized_key = str(key).casefold()
        if not any(part in normalized_key for part in ("location", "country", "city", "name", "code")):
            continue
        cleaned = clean_text(value)
        if cleaned:
            terms.add(cleaned.casefold())
    display_name = _location_display_name(location)
    if display_name:
        terms.add(display_name.casefold())
    if "united arab emirates" in terms:
        terms.add("uae")
    if "ae" in terms:
        terms.add("uae")
    return terms


def _infer_work_location_from_content(
    content: str,
    work_locations: list[dict[str, Any]],
) -> dict[str, Any] | None:
    normalized_content = f" {content.casefold()} "
    matches = []
    for location in work_locations:
        terms = _location_search_terms(location)
        if any(f" {term} " in normalized_content or term in normalized_content for term in terms):
            matches.append(location)
    return matches[0] if len(matches) == 1 else None


def _infer_component_name(content: str) -> str | None:
    patterns = (
        r"\bcalled\s+(.+?)(?:[.,;]|\buse\b|\busing\b|\bwith\b|$)",
        r"\bnamed\s+(.+?)(?:[.,;]|\buse\b|\busing\b|\bwith\b|$)",
        r"\b(?:create|set up|setup|configure)\s+(?:a|an)\s+(.+?)(?:\s+(?:earning|earnings|deduction|deductions|component|pay component)\b|\s+equal\b|\s+with\b|\s+using\b|[.,;]|$)",
    )
    for pattern in patterns:
        match = re.search(pattern, content, flags=re.IGNORECASE)
        if match:
            name = clean_text(match.group(1))
            if name:
                name = re.sub(
                    r"^(taxable|non[-\s]?taxable|fixed|manual|formula|earnings?|deductions?)\s+",
                    "",
                    name,
                    flags=re.IGNORECASE,
                )
            return clean_text(name)
    return None


def _infer_formula_label_and_factor(content: str) -> tuple[str | None, str | None]:
    percent_patterns = (
        r"(\d+(?:\.\d+)?)\s*%\s*(?:of|from)\s+(.+?)(?:[.,;]|$)",
        r"(\d+(?:\.\d+)?)\s+percent\s*(?:of|from)\s+(.+?)(?:[.,;]|$)",
    )
    for pattern in percent_patterns:
        match = re.search(pattern, content, flags=re.IGNORECASE)
        if match:
            label = re.sub(
                r"^(the|a|an)\s+",
                "",
                clean_text(match.group(2)) or "",
                flags=re.IGNORECASE,
            )
            return label or None, clean_text(match.group(1))
    return None, None


def _infer_args_from_content(
    content: str | None,
    context_data: dict[str, Any],
) -> dict[str, Any]:
    text = clean_text(content)
    if not text:
        return {}

    normalized = text.casefold()
    inferred: dict[str, Any] = {}

    name = _infer_component_name(text)
    if name:
        inferred["name"] = name

    if re.search(r"\b(deduction|deductions)\b", normalized):
        inferred["type"] = "DEDUCTION"
    elif re.search(r"\b(earning|earnings|allowance|bonus|salary)\b", normalized):
        inferred["type"] = "EARNINGS"

    if re.search(r"\b(manual|manually|manual input)\b", normalized):
        inferred["calculation_method"] = "MANUAL_INPUT"
    elif re.search(r"\b(formula|%|percent)\b", normalized):
        inferred["calculation_method"] = "FORMULA"
    elif re.search(r"\b(fixed|fixed amount)\b", normalized):
        inferred["calculation_method"] = "FIXED_AMOUNT"

    fixed_amount_match = re.search(
        r"\bfixed(?:\s+amount)?(?:\s+of)?\s+(\d+(?:\.\d+)?)\s*([A-Z]{3})?\b",
        text,
        flags=re.IGNORECASE,
    )
    if fixed_amount_match:
        inferred["default_amount"] = fixed_amount_match.group(1)
        if fixed_amount_match.group(2):
            inferred["currency"] = fixed_amount_match.group(2).upper()

    label, percent = _infer_formula_label_and_factor(text)
    if label:
        inferred["formula_variable_label"] = label
    if percent:
        inferred["formula_percent"] = percent

    currency_match = CURRENCY_PATTERN.search(text)
    if currency_match and "currency" not in inferred:
        inferred["currency"] = currency_match.group(0)

    if re.search(r"\b(non[-\s]?taxable|not taxable|tax exempt)\b", normalized):
        inferred["apply_tax"] = False
        inferred["tax_treatment"] = "NON_TAXABLE"
    elif re.search(r"\btaxable\b", normalized):
        inferred["apply_tax"] = True
        inferred["tax_treatment"] = "TAXABLE"

    if re.search(r"\b(?:do not|don't|not)\s+prorat(?:e|ed|ion)\b|\bnon[-\s]?prorat(?:e|ed|ion)\b", normalized):
        inferred["proration_enabled"] = False
    elif re.search(r"\bprorat(?:e|ed|ion)\b", normalized):
        inferred["proration_enabled"] = True

    selected_location = _infer_work_location_from_content(
        text,
        _work_locations(context_data),
    )
    if selected_location:
        inferred["work_location_id"] = clean_text(_location_value(selected_location, "id"))
        inferred["work_location_name"] = _location_display_name(selected_location)

    return {key: value for key, value in inferred.items() if value is not None}


def _flatten_formula_variables(context_data: dict[str, Any]) -> list[dict[str, Any]]:
    raw = context_data.get("payroll_formula_variables")
    if not isinstance(raw, dict):
        return []

    variables: list[dict[str, Any]] = []
    for group_key, group_variables in raw.items():
        if not isinstance(group_variables, list):
            continue
        for variable in group_variables:
            if not isinstance(variable, dict):
                continue
            value = clean_text(variable.get("value"))
            if not value:
                continue
            variables.append(
                {
                    "group": str(group_key),
                    "label": clean_text(variable.get("label")),
                    "value": value,
                    "data_type": clean_text(
                        _first_value(variable, "data_type", "dataType")
                    ),
                }
            )
    return variables


def _variable_display_label(variable: dict[str, Any]) -> str:
    return (
        clean_text(variable.get("label"))
        or clean_text(variable.get("value"))
        or "Unknown variable"
    )


def _normalized_exact_label(value: str | None) -> str:
    return re.sub(r"\s+", " ", clean_text(value)).casefold()


def _formula_variable_suggestions(
    variables: list[dict[str, Any]],
    requested_label: str | None,
    *,
    limit: int = 5,
) -> list[dict[str, Any]]:
    requested_keys = _label_match_keys(requested_label)
    scored: list[tuple[int, str, dict[str, Any]]] = []

    for variable in variables:
        label = _variable_display_label(variable)
        label_keys = _label_match_keys(label)
        score = 0
        if requested_keys and label_keys:
            if requested_keys & label_keys:
                score += 100
            for requested_key in requested_keys:
                for label_key in label_keys:
                    if requested_key in label_key or label_key in requested_key:
                        score += 25
        data_type = clean_text(variable.get("data_type")) or ""
        if data_type in {"MONEY", "NUMBER", "PAY_COMPONENT"}:
            score += 5
        group = clean_text(variable.get("group")) or ""
        if group in {"pc", "compensation_type", "attendance", "attendance.days", "timeoff", "timeoff.days"}:
            score += 2
        scored.append((score, label.casefold(), variable))

    scored.sort(key=lambda item: (-item[0], item[1]))
    suggestions = []
    seen_labels: set[str] = set()
    for score, _, variable in scored:
        if score <= 0 and requested_keys:
            continue
        label = _variable_display_label(variable)
        if label in seen_labels:
            continue
        seen_labels.add(label)
        suggestions.append(
            {
                "label": label,
                "value": clean_text(variable.get("value")),
                "data_type": clean_text(variable.get("data_type")),
                "group": clean_text(variable.get("group")),
            }
        )
        if len(suggestions) >= limit:
            break

    if suggestions or not requested_keys:
        return suggestions

    for _, _, variable in scored[:limit]:
        suggestions.append(
            {
                "label": _variable_display_label(variable),
                "value": clean_text(variable.get("value")),
                "data_type": clean_text(variable.get("data_type")),
                "group": clean_text(variable.get("group")),
            }
        )
    return suggestions


def _formula_variable_error_result(
    error: str,
    *,
    variables: list[dict[str, Any]],
    requested_label: str | None = None,
    suggestions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    suggestion_payload = suggestions
    if suggestion_payload is None:
        suggestion_payload = _formula_variable_suggestions(variables, requested_label)

    labels = [
        clean_text(suggestion.get("label"))
        for suggestion in suggestion_payload
        if clean_text(suggestion.get("label"))
    ]
    prerequisite_hint = _formula_prerequisite_hint(requested_label)
    if labels:
        if error == "ambiguous_formula_variable_label":
            user_message = (
                "I found multiple possible formula variables. "
                "Ask the user which one to use: "
                + ", ".join(labels)
                + "."
            )
        else:
            user_message = (
                "I could not confidently identify the formula variable. "
                "Ask the user to choose one of these available variables: "
                + ", ".join(labels)
                + "."
            )
    else:
        user_message = (
            "I could not find a matching formula variable in the available payroll variables. "
            "Ask the user which available variable to use."
        )
    if prerequisite_hint and error != "ambiguous_formula_variable_label":
        user_message = f"{user_message} {prerequisite_hint}"

    return {
        "ok": False,
        "error": error,
        "data": {
            "user_message": user_message,
            "suggestions": suggestion_payload,
        },
    }


def _formula_prerequisite_hint(requested_label: str | None) -> str | None:
    words = set(_label_words(requested_label))
    if words & {"salary", "basic", "base", "compensation"}:
        return (
            "If the requested salary or compensation variable is missing, "
            "the compensation type must be configured and active before it can be used in a formula."
        )
    if words & {"leave", "timeoff", "time", "off"}:
        return (
            "If the requested leave variable is missing, "
            "the time-off type must be configured before it can be used in a payroll formula."
        )
    if words & {"component", "allowance", "deduction", "earning", "earnings"}:
        return (
            "If the requested pay component variable is missing, "
            "that component must already exist for the selected location before it can be used in a formula."
        )
    return None


def _label_words(value: str | None) -> list[str]:
    text = clean_text(value)
    if not text:
        return []
    normalized = text.casefold()
    normalized = normalized.replace("&", " and ")
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return [word for word in normalized.split() if word]


def _label_match_keys(value: str | None, *, normalize_aliases: bool = True) -> set[str]:
    text = clean_text(value)
    words = _label_words(text)
    if not words:
        return set()

    keys = {" ".join(words)}
    business_words = [
        "base" if normalize_aliases and word == "basic" else word
        for word in words
        if word not in LOCATION_WORDS
    ]
    if business_words:
        keys.add(" ".join(business_words))

    if "-" in text:
        suffix = text.split("-")[-1].strip()
        keys.update(_label_match_keys(suffix))

    without_prefixes = [
        word
        for word in business_words
        if word not in FORMULA_LABEL_PREFIXES
    ]
    if without_prefixes:
        keys.add(" ".join(without_prefixes))

    return {key for key in keys if key}


def _contains_label_word(value: str | None, word: str) -> bool:
    return word.casefold() in set(_label_words(value))


def _salary_package_candidates(variables: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        variable
        for variable in variables
        if clean_text(variable.get("group")) == "compensation_type"
        and _contains_label_word(_variable_display_label(variable), "salary")
        and clean_text(variable.get("data_type")) in {"MONEY", "NUMBER", "PAY_COMPONENT"}
    ]


def _match_formula_variable_by_label(
    variables: list[dict[str, Any]],
    requested_label: str | None,
) -> tuple[dict[str, Any] | None, str | None, list[dict[str, Any]]]:
    requested_keys = _label_match_keys(requested_label)
    if not requested_keys:
        return None, "pay_component_formula_variable_label_required", []

    exact_label_matches = [
        variable
        for variable in variables
        if _normalized_exact_label(_variable_display_label(variable))
        == _normalized_exact_label(requested_label)
    ]
    if len(exact_label_matches) == 1:
        return exact_label_matches[0], None, []
    if len(exact_label_matches) > 1:
        return (
            None,
            "ambiguous_formula_variable_label",
            _formula_variable_suggestions(exact_label_matches, requested_label),
        )

    literal_requested_keys = _label_match_keys(requested_label, normalize_aliases=False)
    literal_matches = [
        variable
        for variable in variables
        if literal_requested_keys
        and literal_requested_keys & _label_match_keys(
            clean_text(variable.get("label")),
            normalize_aliases=False,
        )
    ]
    if len(literal_matches) == 1:
        return literal_matches[0], None, []
    if len(literal_matches) > 1:
        return (
            None,
            "ambiguous_formula_variable_label",
            _formula_variable_suggestions(literal_matches, requested_label),
        )

    if _contains_label_word(requested_label, "salary"):
        salary_candidates = _salary_package_candidates(variables)
        if len(salary_candidates) > 1:
            return (
                None,
                "ambiguous_formula_variable_label",
                _formula_variable_suggestions(salary_candidates, requested_label),
            )

    exact_matches = [
        variable
        for variable in variables
        if requested_keys & _label_match_keys(clean_text(variable.get("label")))
    ]
    if len(exact_matches) == 1:
        return exact_matches[0], None, []
    if len(exact_matches) > 1:
        return (
            None,
            "ambiguous_formula_variable_label",
            _formula_variable_suggestions(exact_matches, requested_label),
        )

    fuzzy_matches = []
    for variable in variables:
        label = clean_text(variable.get("label"))
        label_keys = _label_match_keys(label)
        if any(
            requested_key in label_key or label_key in requested_key
            for requested_key in requested_keys
            for label_key in label_keys
        ):
            fuzzy_matches.append(variable)

    if len(fuzzy_matches) == 1:
        return fuzzy_matches[0], None, []
    if len(fuzzy_matches) > 1:
        return (
            None,
            "ambiguous_formula_variable_label",
            _formula_variable_suggestions(fuzzy_matches, requested_label),
        )

    return (
        None,
        "unsupported_formula_variable_label",
        _formula_variable_suggestions(variables, requested_label),
    )


def _build_formula_from_variable(
    *,
    variables: list[dict[str, Any]],
    variable_label: str | None,
    percent: Decimal | None,
    multiplier: Decimal | None,
) -> tuple[str | None, str | None, list[dict[str, Any]]]:
    variable, error, suggestions = _match_formula_variable_by_label(variables, variable_label)
    if error:
        return None, error, suggestions
    if variable is None:
        return None, "unsupported_formula_variable_label", suggestions

    token = clean_text(variable.get("value"))
    if not token:
        return None, "unsupported_formula_variable_label", suggestions

    factor = multiplier
    if factor is None and percent is not None:
        factor = percent / Decimal("100")
    if factor is None:
        factor = Decimal("1")

    if factor == Decimal("1"):
        return token, None, []
    return f"{token} * {_formula_decimal_text(factor)}", None, []


def _formula_tokens(formula: str) -> list[str]:
    return [f"${{{match}}}" for match in FORMULA_TOKEN_PATTERN.findall(formula)]


def _has_balanced_parentheses(value: str) -> bool:
    depth = 0
    for char in value:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        if depth < 0:
            return False
    return depth == 0


def _validate_formula(
    *,
    formula: str,
    variables: list[dict[str, Any]],
    current_pay_component_id: str | None,
) -> str | None:
    tokens = _formula_tokens(formula)
    if not tokens:
        return "pay_component_formula_variable_required"

    if not variables:
        return "payroll_formula_variables_required_for_formula"

    supported_values = {
        value
        for value in (clean_text(variable.get("value")) for variable in variables)
        if value
    }
    unsupported = sorted({token for token in tokens if token not in supported_values})
    if unsupported:
        return f"unsupported_formula_variable: {', '.join(unsupported)}"

    if current_pay_component_id and f"${{pc.{current_pay_component_id}}}" in tokens:
        return "pay_component_formula_cannot_reference_itself"

    without_variables = FORMULA_TOKEN_PATTERN.sub("1", formula)
    if not FORMULA_ALLOWED_PATTERN.match(without_variables):
        return "invalid_formula_syntax"
    if not _has_balanced_parentheses(without_variables):
        return "invalid_formula_parentheses"
    if re.search(r"/\s*0(?:\.0+)?(?:\D|$)", without_variables):
        return "division_by_zero"

    return None


async def run(task_args, context: RequestContext, http_client: HttpClient):
    del http_client

    task_args = task_args if isinstance(task_args, dict) else {}
    context_data = _client_context_data(context)
    inferred_args = _infer_args_from_content(
        _first_value(task_args, "content", "request", "prompt"),
        context_data,
    )
    task_args = {**inferred_args, **task_args}
    current = _current_pay_component(context_data)
    work_locations = _work_locations(context_data)

    name = clean_text(_first_value(task_args, "name", "component_name", "componentName"))
    if not name:
        name = clean_text(_context_value(current, "name"))

    work_location_id = clean_text(
        _first_value(task_args, "work_location_id", "workLocationId", "location_id", "locationId")
    )
    if not work_location_id:
        work_location_id = clean_text(_context_value(current, "work_location_id", "workLocationId"))

    work_location_name = clean_text(
        _first_value(task_args, "work_location_name", "workLocationName", "location_name", "locationName")
    )
    if not work_location_name:
        work_location_name = clean_text(
            _context_value(current, "work_location_name", "workLocationName")
        )

    selected_work_location = _match_work_location_by_id(
        work_locations, work_location_id
    )
    if not selected_work_location and work_location_name:
        selected_work_location = _match_work_location_by_name(
            work_locations, work_location_name
        )
        if selected_work_location:
            work_location_id = clean_text(_location_value(selected_work_location, "id"))

    if not selected_work_location and not work_location_id and len(work_locations) == 1:
        selected_work_location = work_locations[0]
        work_location_id = clean_text(_location_value(selected_work_location, "id"))

    if "payroll_work_locations" in context_data and not work_location_id:
        return _location_required_error_result(work_locations)

    if work_locations and work_location_id and not selected_work_location:
        return error_result("unsupported_pay_component_work_location")

    if selected_work_location and not work_location_name:
        work_location_name = _location_display_name(selected_work_location)

    component_type = _clean_enum(
        _first_value(task_args, "type", "component_type", "componentType"),
        PAY_COMPONENT_TYPES,
    )
    if not component_type:
        component_type = _clean_enum(_context_value(current, "type"), PAY_COMPONENT_TYPES)

    description = clean_text(_first_value(task_args, "description"))
    if not description:
        description = clean_text(_context_value(current, "description"))

    calculation_method = _clean_enum(
        _first_value(task_args, "calculation_method", "calculationMethod", "amount_setup", "amountSetup"),
        CALCULATION_METHODS,
    )
    if not calculation_method:
        calculation_method = _clean_enum(
            _context_value(current, "calculation_method", "calculationMethod"),
            CALCULATION_METHODS,
        )

    default_amount = _clean_decimal(
        _first_value(task_args, "default_amount", "defaultAmount", "amount")
    )
    if default_amount is None:
        default_amount = _clean_decimal(_context_value(current, "default_amount", "defaultAmount"))

    currency = clean_text(_first_value(task_args, "currency"))
    if not currency:
        currency = clean_text(_context_value(current, "currency"))
    if not currency and selected_work_location:
        currency = clean_text(_location_value(selected_work_location, "currency"))

    formula = clean_text(_first_value(task_args, "formula"))
    if not formula:
        formula = clean_text(_context_value(current, "formula"))

    formula_variable_label = clean_text(
        _first_value(
            task_args,
            "formula_variable_label",
            "formulaVariableLabel",
            "formula_source_label",
            "formulaSourceLabel",
        )
    )
    formula_percent = _clean_decimal(
        _first_value(task_args, "formula_percent", "formulaPercent", "percent")
    )
    formula_multiplier = _clean_decimal(
        _first_value(task_args, "formula_multiplier", "formulaMultiplier", "multiplier")
    )

    apply_tax = _clean_bool(_first_value(task_args, "apply_tax", "applyTax"))
    if apply_tax is None:
        apply_tax = _clean_bool(_context_value(current, "apply_tax", "applyTax")) or False

    tax_treatment = _clean_enum(
        _first_value(task_args, "tax_treatment", "taxTreatment"),
        TAX_TREATMENTS,
    )
    if not tax_treatment:
        tax_treatment = _clean_enum(_context_value(current, "tax_treatment", "taxTreatment"), TAX_TREATMENTS)

    proration_enabled = _clean_bool(
        _first_value(task_args, "proration_enabled", "prorationEnabled")
    )
    if proration_enabled is None:
        proration_enabled = _clean_bool(
            _context_value(current, "proration_enabled", "prorationEnabled")
        )

    proration_rule_override_id = clean_text(
        _first_value(task_args, "proration_rule_override_id", "prorationRuleOverrideId")
    )
    if not proration_rule_override_id:
        proration_rule_override_id = clean_text(
            _context_value(current, "proration_rule_override_id", "prorationRuleOverrideId")
        )

    if not calculation_method:
        return error_result("pay_component_calculation_method_required")

    if calculation_method == "FIXED_AMOUNT":
        if default_amount is None:
            return error_result("pay_component_default_amount_required")
        if default_amount < 0:
            return error_result("pay_component_default_amount_must_be_non_negative")
        if not currency:
            return error_result("pay_component_currency_required")
        formula = None

    if calculation_method == "FORMULA":
        variables = _flatten_formula_variables(context_data)
        if not formula and formula_variable_label:
            formula, formula_build_error, variable_suggestions = _build_formula_from_variable(
                variables=variables,
                variable_label=formula_variable_label,
                percent=formula_percent,
                multiplier=formula_multiplier,
            )
            if formula_build_error:
                return _formula_variable_error_result(
                    formula_build_error,
                    variables=variables,
                    requested_label=formula_variable_label,
                    suggestions=variable_suggestions,
                )
        if not formula:
            return _formula_variable_error_result(
                "pay_component_formula_required",
                variables=variables,
                requested_label=formula_variable_label,
            )
        validation_error = _validate_formula(
            formula=formula,
            variables=variables,
            current_pay_component_id=clean_text(_context_value(current, "id")),
        )
        if validation_error:
            if validation_error.startswith("unsupported_formula_variable"):
                return _formula_variable_error_result(
                    validation_error,
                    variables=variables,
                    requested_label=formula_variable_label,
                )
            return error_result(validation_error)
        default_amount = None
        currency = None
        if proration_enabled is None:
            proration_enabled = True

    if calculation_method == "MANUAL_INPUT":
        default_amount = None
        currency = None
        formula = None
        proration_enabled = False
        proration_rule_override_id = None

    if calculation_method != "FORMULA":
        proration_enabled = False
        proration_rule_override_id = None

    payload = {
        "name": name or None,
        "work_location_id": work_location_id or None,
        "work_location_name": work_location_name or None,
        "type": component_type or None,
        "description": description or None,
        "calculation_method": calculation_method,
        "default_amount": _normalize_number(default_amount),
        "currency": currency or None,
        "formula": formula or None,
        "apply_tax": apply_tax,
        "tax_treatment": tax_treatment if apply_tax else None,
        "proration_enabled": bool(proration_enabled),
        "proration_rule_override_id": proration_rule_override_id or None,
    }

    result_data = {"content": payload, "action": ACTION_NAME}
    assistant_message = clean_text(
        _first_value(task_args, "assistant_message", "assistantMessage")
    )
    if assistant_message:
        result_data["assistant_message"] = assistant_message

    return ok_result(result_data)
