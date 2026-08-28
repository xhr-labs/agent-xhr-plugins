from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from src.application.employee.search_employees import run as search_employees_run
from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.core.models.types import Header
from src.shared.normalize import clean_text, clean_int, to_bool
from src.shared.result import ok_result, error_result


def _parse_iso(value):
    if not value:
        return None
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        try:
            return datetime.fromisoformat(raw)
        except Exception:
            return None
    return None


def _pick_earliest_slot(slots):
    if not isinstance(slots, list):
        return None

    candidates = []
    for slot in slots:
        if not isinstance(slot, dict):
            continue
        start = slot.get("start")
        parsed = _parse_iso(start)
        if parsed:
            candidates.append((parsed, slot))

    if candidates:
        candidates.sort(key=lambda item: item[0])
        return candidates[0][1]

    for slot in slots:
        if isinstance(slot, dict) and slot.get("start"):
            return slot

    return None


def _availability_tzinfo(tz_name, slots):
    if tz_name:
        try:
            return ZoneInfo(tz_name)
        except Exception:
            pass
    for slot in slots or []:
        if not isinstance(slot, dict):
            continue
        parsed = _parse_iso(slot.get("start"))
        if parsed is not None and parsed.tzinfo is not None:
            return parsed.tzinfo
    return None


def _normalize_slot_bound(value, default_tz=None):
    parsed = _parse_iso(value)
    if parsed is None:
        return value
    if parsed.tzinfo is None and default_tz is not None:
        parsed = parsed.replace(tzinfo=default_tz)
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc)
    return parsed.isoformat()


def _slot_key(slot, default_tz=None):
    if not isinstance(slot, dict):
        return None
    start_key = _normalize_slot_bound(slot.get("start"), default_tz)
    end_key = _normalize_slot_bound(slot.get("end"), default_tz)
    if not start_key or not end_key:
        return None
    return (start_key, end_key)


def _filter_mutual_slots(primary_slots, secondary_slots, default_tz=None):
    if not isinstance(primary_slots, list) or not isinstance(secondary_slots, list):
        return []

    secondary_keys = {
        key for key in (_slot_key(slot, default_tz) for slot in secondary_slots)
        if key is not None
    }
    if not secondary_keys:
        return []

    mutual = []
    for slot in primary_slots:
        if _slot_key(slot, default_tz) in secondary_keys:
            mutual.append(slot)
    return mutual


def _normalize_employee(item):
    if not isinstance(item, dict):
        return None

    employee_id = clean_text(item.get("id") or item.get("employee_id"))
    if not employee_id:
        return None

    def display_value(value):
        if isinstance(value, dict):
            value = value.get("name") or value.get("label")
        return clean_text(value)

    employee = {
        "employee_id": employee_id,
        "name": clean_text(
            item.get("name") or item.get("full_name") or item.get("display_name")
        ),
        "email": clean_text(item.get("work_email") or item.get("email")),
        "department": display_value(item.get("department")),
        "job_title": display_value(item.get("job_title") or item.get("position")),
        "location": display_value(item.get("work_location") or item.get("location")),
    }
    return {key: value for key, value in employee.items() if value is not None}


async def _resolve_colleague_name(
    colleague_name,
    context: RequestContext,
    http_client: HttpClient,
):
    result = await search_employees_run(
        {"name": colleague_name, "includeLineManager": False},
        context,
        http_client,
    )
    if not result.get("ok"):
        return result

    payload = result.get("data") or {}
    items = payload.get("data") or []
    if isinstance(items, dict):
        items = [items]
    if not isinstance(items, list):
        items = []

    candidates = []
    for item in items:
        employee = _normalize_employee(item)
        if employee:
            candidates.append(employee)

    if not candidates:
        return error_result(f"colleague_name_not_found:{colleague_name}")

    return {
        "ok": True,
        "candidates": candidates,
    }


async def _fetch_availability(client, availability_url, payload, headers):
    response = await client.post(
        availability_url,
        json=payload,
        headers=headers,
    )
    try:
        body = response.json()
    except Exception:
        body = {"message": response.text}
    finally:
        await response.aclose()

    status = response.status_code
    if isinstance(body, dict):
        data = body.get("data") or {}
    else:
        data = {}
    slots = data.get("slots")
    if not isinstance(slots, list):
        slots = []
    return status, body, data, slots


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers
    request_headers = context.request_headers

    task_args = task_args if isinstance(task_args, dict) else {}

    colleague_id = clean_text(
        task_args.get("colleagueId")
        or task_args.get("employeeId")
        or task_args.get("colleague_id")
        or task_args.get("employee_id")
    )
    colleague_name = clean_text(
        task_args.get("colleagueName")
        or task_args.get("employeeName")
        or task_args.get("colleague_name")
        or task_args.get("employee_name")
    )
    requester_id = clean_text(request_headers.get(Header.X_EMPLOYEE_ID))
    duration_minutes = clean_int(
        task_args.get("durationMinutes") or task_args.get("duration_minutes")
    )
    range_start = clean_text(task_args.get("rangeStart") or task_args.get("range_start"))
    range_end = clean_text(task_args.get("rangeEnd") or task_args.get("range_end"))
    buffer_minutes = clean_int(
        task_args.get("bufferMinutes") or task_args.get("buffer_minutes")
    )
    min_notice_minutes = clean_int(
        task_args.get("minNoticeMinutes") or task_args.get("min_notice_minutes")
    )
    limit = clean_int(task_args.get("limit"))
    confirm = to_bool(task_args.get("confirm"))
    slot_start = clean_text(task_args.get("slotStart") or task_args.get("slot_start"))
    slot_end = clean_text(task_args.get("slotEnd") or task_args.get("slot_end"))
    notes = task_args.get("notes")
    if isinstance(notes, str):
        notes = notes.strip() or None
    else:
        notes = None

    time_zone = (
        clean_text(
            request_headers.get("x-timezone")
            or request_headers.get("x-time-zone")
        )
        or "UTC"
    )

    if not range_start or not range_end:
        today = datetime.utcnow().date()
        if not range_start:
            range_start = today.isoformat()
        if not range_end:
            range_end = (today + timedelta(days=10)).isoformat()

    missing_fields = []
    if not colleague_id and not colleague_name:
        missing_fields.append("colleagueId or colleagueName")
    if not requester_id:
        missing_fields.append("xhr-employee-id header")
    # Duration is only needed once availability is queried (steps 2 and 3);
    # resolving a colleague by name must work before the user has picked one.
    if colleague_id and duration_minutes is None:
        missing_fields.append("durationMinutes")
    if missing_fields:
        return error_result(f"Missing required fields: {', '.join(missing_fields)}",)

    if bool(slot_start) != bool(slot_end):
        return error_result("slotStart and slotEnd must be provided together")
    if confirm and not slot_start:
        return error_result(
            "Missing required fields for confirmed booking: slotStart, slotEnd"
        )

    if not colleague_id:
        resolution = await _resolve_colleague_name(
            colleague_name,
            context,
            http_client,
        )
        if not resolution.get("ok"):
            return resolution

        return ok_result({
            "data": {"candidates": resolution.get("candidates") or []},
            "nextAction": "confirm_colleague_selection",
            "query": {"name": colleague_name},
        })

    availability_payload = {
        "duration_minutes": duration_minutes,
        "range_start": range_start,
        "range_end": range_end,
        "time_zone": time_zone,
    }
    if buffer_minutes is not None:
        availability_payload["buffer_minutes"] = buffer_minutes
    if min_notice_minutes is not None:
        availability_payload["min_notice_minutes"] = min_notice_minutes
    if limit is not None:
        availability_payload["limit"] = limit

    availability_url = f"{api_base_url}/v1/cls/availability/slots"

    async with http_client.session() as client:
        colleague_payload = dict(availability_payload)
        colleague_payload["employee_id"] = colleague_id
        availability_status, availability_body, availability_data, colleague_slots = (
            await _fetch_availability(
                client,
                availability_url,
                colleague_payload,
                headers,
            )
        )
        if availability_status < 200 or availability_status >= 300:
            return error_result(f"availability_lookup_failed: {availability_status} {str(availability_body)}",)

        if requester_id == colleague_id:
            requester_payload = None
            requester_slots = colleague_slots
        else:
            requester_payload = dict(availability_payload)
            requester_payload["employee_id"] = requester_id
            requester_status, requester_body, _requester_data, requester_slots = (
                await _fetch_availability(
                    client,
                    availability_url,
                    requester_payload,
                    headers,
                )
            )
            if requester_status < 200 or requester_status >= 300:
                return error_result(f"requester_availability_lookup_failed: {requester_status} {str(requester_body)}",)

        # A slot passed without an offset means wall-clock time in the
        # availability timezone; normalize both sides to UTC instants so the
        # comparison never depends on how the datetime string was formatted.
        slot_tz = _availability_tzinfo(
            availability_data.get("time_zone") or time_zone,
            colleague_slots,
        )

        mutual_slots = _filter_mutual_slots(colleague_slots, requester_slots, slot_tz)

        if slot_start and slot_end:
            requested_key = _slot_key({"start": slot_start, "end": slot_end}, slot_tz)
            selected_slot = next(
                (slot for slot in mutual_slots if _slot_key(slot, slot_tz) == requested_key),
                None,
            )
            if not selected_slot:
                result = error_result(
                    f"requested_slot_not_available:{slot_start}/{slot_end}"
                )
                result["data"] = {
                    "timeZone": availability_data.get("time_zone") or time_zone,
                    "slots": mutual_slots,
                    "nextAction": "confirm_booking_with_user",
                }
                return result
        else:
            selected_slot = _pick_earliest_slot(mutual_slots)

        if not selected_slot:
            return ok_result({
                "data": {
                    "timeZone": availability_data.get("time_zone") or time_zone,
                    "slots": mutual_slots,
                    "selectedSlot": None,
                },
                "nextAction": "no_mutual_slots_available",
                "meta": {
                    "colleagueAvailabilityPayload": colleague_payload,
                    "requesterAvailabilityPayload": requester_payload,
                    "colleagueSlots": colleague_slots,
                    "requesterSlots": requester_slots,
                },
                "query": {"availabilityEndpoint": availability_url},
            })

        selected_start = selected_slot.get("start")
        selected_end = selected_slot.get("end")
        if not selected_start or not selected_end:
            return error_result("selected_slot_missing_bounds",)

        if not confirm:
            return ok_result({
                "data": {
                    "colleagueId": colleague_id,
                    "colleagueName": colleague_name,
                    "requesterId": requester_id,
                    "timeZone": availability_data.get("time_zone") or time_zone,
                    "selectedSlot": selected_slot,
                    "slots": mutual_slots,
                },
                "nextAction": "confirm_booking_with_user",
                "meta": {
                    "colleagueAvailabilityPayload": colleague_payload,
                    "requesterAvailabilityPayload": requester_payload,
                },
                "query": {"availabilityEndpoint": availability_url},
            })

        booking_payload = {
            "owner_employee_id": colleague_id,
            "start": selected_start,
            "end": selected_end,
            "notes": notes,
        }
        booking_payload = {
            key: value for key, value in booking_payload.items()
            if value is not None
        }

        booking_headers = dict(headers)
        booking_headers["x-timezone"] = time_zone
        booking_url = f"{api_base_url}/v1/cls/appointments/direct"
        booking_response = await client.post(
            booking_url,
            json=booking_payload,
            headers=booking_headers,
        )
        try:
            booking_body = booking_response.json()
        except Exception:
            booking_body = {"message": booking_response.text}
        finally:
            await booking_response.aclose()

    booking_status = booking_response.status_code
    success = 200 <= booking_status < 300
    next_action = "meeting_booked" if success else "booking_failed"

    if not success:
        return error_result(f"booking_failed: {booking_status} {str(booking_body)}",)

    return ok_result({
        "data": {
            "colleagueId": colleague_id,
            "colleagueName": colleague_name,
            "requesterId": requester_id,
            "timeZone": availability_data.get("time_zone") or time_zone,
            "selectedSlot": selected_slot,
            "bookingResponse": booking_body,
        },
        "nextAction": next_action,
        "meta": {
            "colleagueAvailabilityPayload": colleague_payload,
            "requesterAvailabilityPayload": requester_payload,
            "bookingPayload": booking_payload,
        },
        "query": {
            "availabilityEndpoint": availability_url,
            "bookingEndpoint": booking_url,
        },
    })
