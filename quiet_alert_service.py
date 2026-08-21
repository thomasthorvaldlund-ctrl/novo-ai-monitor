import fcntl
import json
import os
from datetime import datetime, timezone
from pathlib import Path


STATE_VERSION = 1
SEVERITY_RANK = {
    "low": 1,
    "moderate": 2,
    "high": 3,
    "critical": 4,
}
ACTION_LABELS = {
    "opened": "Ny alarm",
    "escalated": "Forværret alarm",
    "updated": "Væsentligt ændret",
    "reminder": "Fortsat aktiv",
    "recovered": "Afsluttet",
}


class QuietAlertError(RuntimeError):
    pass


def _normalise_now(now=None):
    value = now or datetime.now(timezone.utc)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _timestamp(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _hours_since(value, now):
    parsed = _timestamp(value)
    if parsed is None:
        return float("inf")
    return max(0.0, (now - parsed).total_seconds() / 3600)


def _load_state(path):
    if not path.exists():
        return {"version": STATE_VERSION, "events": {}}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise QuietAlertError("Alarmtilstanden kunne ikke læses.") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("events"), dict):
        raise QuietAlertError("Alarmtilstanden har ugyldigt format.")
    if payload.get("version") != STATE_VERSION:
        raise QuietAlertError("Alarmtilstanden har ukendt version.")
    return payload


def _write_state(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, sort_keys=True, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.chmod(temporary, 0o600)
    temporary.replace(path)
    os.chmod(path, 0o600)


def _validate_event(event):
    if not isinstance(event, dict):
        raise ValueError("Hver alarmhændelse skal være et dictionary.")
    key = str(event.get("key", "")).strip()
    if not key:
        raise ValueError("Alarmhændelsen mangler key.")
    if not isinstance(event.get("active"), bool):
        raise ValueError("Alarmhændelsens active skal være boolsk.")
    severity = str(event.get("severity", "low")).strip().lower()
    if severity not in SEVERITY_RANK:
        raise ValueError("Alarmhændelsen har ukendt severity.")
    return {
        **event,
        "key": key,
        "severity": severity,
        "fingerprint": str(event.get("fingerprint", "")).strip(),
        "title": str(event.get("title", "Alarm")).strip() or "Alarm",
        "body": str(event.get("body", "")).strip(),
    }


def process_alert_events(
    events,
    *,
    path,
    now=None,
    reminder_hours=72,
    changed_hours=24,
):
    if reminder_hours < 1 or changed_hours < 1:
        raise ValueError("Cooldown skal være mindst én time.")
    normalized_events = [_validate_event(event) for event in events]
    state_path = Path(path)
    lock_path = state_path.with_suffix(state_path.suffix + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    current_time = _normalise_now(now)
    current_text = current_time.isoformat(timespec="seconds")
    decisions = []

    with lock_path.open("a+", encoding="utf-8") as lock_handle:
        os.chmod(lock_path, 0o600)
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
        state = _load_state(state_path)
        records = state["events"]

        for event in normalized_events:
            previous = records.get(event["key"], {})
            was_active = bool(previous.get("active"))
            action = None

            if event["active"]:
                if not was_active:
                    action = "opened"
                elif (
                    SEVERITY_RANK[event["severity"]]
                    > SEVERITY_RANK.get(previous.get("notified_severity", "low"), 1)
                ):
                    action = "escalated"
                elif (
                    event["fingerprint"]
                    and event["fingerprint"] != previous.get("notified_fingerprint", "")
                    and _hours_since(previous.get("last_notified_at"), current_time)
                    >= changed_hours
                ):
                    action = "updated"
                elif (
                    _hours_since(previous.get("last_notified_at"), current_time)
                    >= reminder_hours
                ):
                    action = "reminder"
            elif was_active:
                action = "recovered"

            record = {
                **previous,
                "active": event["active"],
                "severity": event["severity"],
                "fingerprint": event["fingerprint"],
                "title": event["title"],
                "last_seen_at": current_text,
            }

            if action:
                record["last_notified_at"] = current_text
                record["notified_fingerprint"] = event["fingerprint"]
                record["notified_severity"] = event["severity"]
                decisions.append({**event, "action": action})

            records[event["key"]] = record

        state["updated_at"] = current_text
        _write_state(state_path, state)
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)

    return decisions


def format_alert_digest(decisions, *, max_length=3800):
    if not decisions:
        return ""
    if all(item.get("action") == "recovered" for item in decisions):
        header = "✅ AUREUM-ALARM AFSLUTTET"
    elif any(item.get("severity") == "critical" for item in decisions):
        header = "🚨 KRITISK AUREUM-VARSEL"
    else:
        header = "⚠️ AUREUM-VARSEL"

    sections = [header]
    for item in decisions:
        label = ACTION_LABELS.get(item.get("action"), "Status")
        body = item.get("body", "")
        section = f"{label}: {item.get('title', 'Alarm')}"
        if body:
            section += f"\n{body}"
        sections.append(section)

    message = "\n\n".join(sections)
    if len(message) > max_length:
        message = message[: max_length - 2].rstrip() + "…"
    return message
