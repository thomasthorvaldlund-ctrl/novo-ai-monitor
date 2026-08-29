import fcntl
import hashlib
import json
import os
import re
import tempfile
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests


STATE_VERSION = 1
ELIGIBLE_ACTIONS = frozenset({"opened", "escalated"})
ELIGIBLE_PREFIXES = ("market:", "earnings:", "ai-news:")
TRUE_VALUES = frozenset({"1", "true", "yes", "on"})
MAX_SMS_LENGTH = 160
MAX_ATTEMPTS = 6
MAX_ATTEMPTS_PER_RUN = 3
DUPLICATE_WINDOW = timedelta(hours=1)
RETRY_DELAY = timedelta(minutes=30)
SENT_RETENTION = timedelta(days=180)

ACCOUNT_SID_PATTERN = re.compile(r"^AC[0-9a-fA-F]{32}$")
API_KEY_PATTERN = re.compile(r"^SK[0-9a-fA-F]{32}$")
MESSAGING_SERVICE_PATTERN = re.compile(r"^MG[0-9a-fA-F]{32}$")
MESSAGE_SID_PATTERN = re.compile(r"^(SM|MM)[0-9a-fA-F]{32}$")
E164_PATTERN = re.compile(r"^\+[1-9][0-9]{7,14}$")
ALPHANUMERIC_SENDER_PATTERN = re.compile(r"^[A-Za-z0-9 ]{1,11}$")


class CriticalSmsError(RuntimeError):
    pass


class CriticalSmsConfigurationError(CriticalSmsError):
    def __init__(self, fields):
        self.fields = tuple(sorted(set(fields)))
        super().__init__("SMS-konfigurationen er ufuldstændig.")


class CriticalSmsProviderError(CriticalSmsError):
    def __init__(self, code, *, retryable):
        self.code = str(code)
        self.retryable = bool(retryable)
        super().__init__("SMS-udbyderen afviste anmodningen.")


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


def _time_text(value):
    return value.isoformat(timespec="seconds")


def _configuration(environ):
    enabled = str(
        environ.get("AUREUM_CRITICAL_SMS_ENABLED", "")
    ).strip().lower() in TRUE_VALUES

    if not enabled:
        return {"enabled": False}

    account_sid = str(environ.get("TWILIO_ACCOUNT_SID", "")).strip()
    api_key_sid = str(environ.get("TWILIO_API_KEY_SID", "")).strip()
    api_key_secret = str(environ.get("TWILIO_API_KEY_SECRET", "")).strip()
    auth_token = str(environ.get("TWILIO_AUTH_TOKEN", "")).strip()
    recipient = str(environ.get("AUREUM_CRITICAL_SMS_TO", "")).strip()
    sender = str(environ.get("TWILIO_SMS_FROM", "")).strip()
    messaging_service = str(
        environ.get("TWILIO_MESSAGING_SERVICE_SID", "")
    ).strip()

    errors = []

    if not ACCOUNT_SID_PATTERN.fullmatch(account_sid):
        errors.append("TWILIO_ACCOUNT_SID")

    key_pair_present = bool(api_key_sid or api_key_secret)

    if key_pair_present:
        if not API_KEY_PATTERN.fullmatch(api_key_sid):
            errors.append("TWILIO_API_KEY_SID")
        if not api_key_secret:
            errors.append("TWILIO_API_KEY_SECRET")
        auth = (api_key_sid, api_key_secret)
    elif auth_token:
        auth = (account_sid, auth_token)
    else:
        errors.append("TWILIO_API_CREDENTIALS")
        auth = ("", "")

    if not E164_PATTERN.fullmatch(recipient):
        errors.append("AUREUM_CRITICAL_SMS_TO")

    if bool(sender) == bool(messaging_service):
        errors.append("TWILIO_SENDER")

    if messaging_service and not MESSAGING_SERVICE_PATTERN.fullmatch(
        messaging_service
    ):
        errors.append("TWILIO_MESSAGING_SERVICE_SID")

    if sender and not (
        E164_PATTERN.fullmatch(sender)
        or ALPHANUMERIC_SENDER_PATTERN.fullmatch(sender)
    ):
        errors.append("TWILIO_SMS_FROM")

    if errors:
        raise CriticalSmsConfigurationError(errors)

    return {
        "enabled": True,
        "account_sid": account_sid,
        "auth": auth,
        "recipient": recipient,
        "sender": sender,
        "messaging_service": messaging_service,
    }


def _ascii_text(value):
    translated = str(value or "").translate(
        str.maketrans(
            {
                "æ": "ae",
                "ø": "oe",
                "å": "aa",
                "Æ": "AE",
                "Ø": "OE",
                "Å": "AA",
            }
        )
    )
    normalised = unicodedata.normalize("NFKD", translated)
    ascii_value = normalised.encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_value.split())


def format_critical_sms(decision, *, max_length=MAX_SMS_LENGTH):
    if max_length < 40 or max_length > MAX_SMS_LENGTH:
        raise ValueError("SMS-laengden er ugyldig.")

    action = str(decision.get("action", "")).strip().lower()
    label = "NY" if action == "opened" else "FORVAERRET"
    title = _ascii_text(decision.get("title", "Alarm")) or "Alarm"
    body = _ascii_text(decision.get("body", ""))

    message = f"AUREUM KRITISK | {label} | {title}"
    if body:
        message += f" | {body}"

    if len(message) > max_length:
        message = message[: max_length - 3].rstrip() + "..."

    return message


def _eligible_decisions(decisions):
    selected = []

    for decision in decisions or ():
        if not isinstance(decision, dict):
            continue
        key = str(decision.get("key", "")).strip()
        severity = str(decision.get("severity", "")).strip().lower()
        action = str(decision.get("action", "")).strip().lower()
        if (
            key.startswith(ELIGIBLE_PREFIXES)
            and severity == "critical"
            and action in ELIGIBLE_ACTIONS
        ):
            selected.append(decision)

    return selected


def _dedupe_key(decision):
    payload = {
        "key": str(decision.get("key", "")).strip(),
        "action": str(decision.get("action", "")).strip().lower(),
        "fingerprint": str(decision.get("fingerprint", "")).strip(),
    }
    encoded = json.dumps(
        payload,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _default_state():
    return {"version": STATE_VERSION, "deliveries": {}}


def _load_state(path):
    if not path.exists():
        return _default_state()
    if path.is_symlink():
        raise CriticalSmsError("SMS-tilstanden maa ikke vaere et symlink.")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CriticalSmsError("SMS-tilstanden kunne ikke laeses.") from exc
    if (
        not isinstance(payload, dict)
        or payload.get("version") != STATE_VERSION
        or not isinstance(payload.get("deliveries"), dict)
    ):
        raise CriticalSmsError("SMS-tilstanden har ugyldigt format.")
    return payload


def _write_state(path, payload):
    if path.exists() and path.is_symlink():
        raise CriticalSmsError("SMS-tilstanden maa ikke vaere et symlink.")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(
                payload,
                handle,
                ensure_ascii=True,
                sort_keys=True,
                indent=2,
            )
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o600)
        temporary.replace(path)
        os.chmod(path, 0o600)
    finally:
        if temporary.exists():
            temporary.unlink()


def _open_lock(path):
    if path.exists() and path.is_symlink():
        raise CriticalSmsError("SMS-laasen maa ikke vaere et symlink.")
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_RDWR | os.O_CREAT
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    os.fchmod(descriptor, 0o600)
    return os.fdopen(descriptor, "a+", encoding="utf-8")


def _prune(deliveries, now):
    for delivery_id, record in list(deliveries.items()):
        if not isinstance(record, dict):
            deliveries.pop(delivery_id, None)
            continue
        created = _timestamp(record.get("created_at"))
        if (
            record.get("status") in {"accepted", "failed"}
            and created is not None
            and now - created > SENT_RETENTION
        ):
            deliveries.pop(delivery_id, None)


def _is_recent_duplicate(deliveries, dedupe_key, now):
    for record in deliveries.values():
        if not isinstance(record, dict):
            continue
        if record.get("dedupe_key") != dedupe_key:
            continue
        created = _timestamp(record.get("created_at"))
        if created is None:
            continue
        if now - created <= DUPLICATE_WINDOW:
            return True
    return False


def _new_delivery_id(dedupe_key, now, deliveries):
    counter = len(deliveries)
    material = f"{dedupe_key}:{_time_text(now)}:{counter}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def _send_twilio(config, message, client):
    url = (
        "https://api.twilio.com/2010-04-01/Accounts/"
        f"{config['account_sid']}/Messages.json"
    )
    data = {
        "To": config["recipient"],
        "Body": message,
        "ValidityPeriod": "900",
    }
    if config["messaging_service"]:
        data["MessagingServiceSid"] = config["messaging_service"]
    else:
        data["From"] = config["sender"]

    try:
        response = client.post(
            url,
            auth=config["auth"],
            data=data,
            timeout=(3.05, 10),
        )
    except requests.RequestException as exc:
        raise CriticalSmsProviderError(
            "network",
            retryable=True,
        ) from exc

    status_code = int(response.status_code)
    if status_code < 200 or status_code >= 300:
        raise CriticalSmsProviderError(
            f"http_{status_code}",
            retryable=(status_code == 429 or status_code >= 500),
        )

    try:
        payload = response.json()
    except (ValueError, TypeError) as exc:
        raise CriticalSmsProviderError(
            "invalid_json",
            retryable=True,
        ) from exc

    message_sid = str(payload.get("sid", "")).strip()
    provider_status = str(payload.get("status", "")).strip().lower()

    if not MESSAGE_SID_PATTERN.fullmatch(message_sid):
        raise CriticalSmsProviderError(
            "invalid_message_sid",
            retryable=True,
        )

    return message_sid, provider_status or "accepted"


def dispatch_critical_sms(
    decisions,
    *,
    path,
    environ=None,
    session=None,
    now=None,
):
    environment = os.environ if environ is None else environ
    selected = _eligible_decisions(decisions)

    try:
        config = _configuration(environment)
    except CriticalSmsConfigurationError as exc:
        return {
            "enabled": True,
            "status": "misconfigured",
            "configuration_errors": list(exc.fields),
            "eligible": len(selected),
            "enqueued": 0,
            "attempted": 0,
            "accepted": 0,
            "pending": 0,
            "failed": 0,
        }

    if not config["enabled"]:
        return {
            "enabled": False,
            "status": "disabled",
            "eligible": len(selected),
            "enqueued": 0,
            "attempted": 0,
            "accepted": 0,
            "pending": 0,
            "failed": 0,
        }

    current_time = _normalise_now(now)
    current_text = _time_text(current_time)
    state_path = Path(path)
    lock_path = state_path.with_suffix(state_path.suffix + ".lock")
    client = requests if session is None else session

    enqueued = 0
    attempted = 0
    accepted = 0
    failed = 0

    with _open_lock(lock_path) as lock_handle:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
        state = _load_state(state_path)
        deliveries = state["deliveries"]
        _prune(deliveries, current_time)

        for decision in selected:
            dedupe_key = _dedupe_key(decision)
            if _is_recent_duplicate(deliveries, dedupe_key, current_time):
                continue
            delivery_id = _new_delivery_id(
                dedupe_key,
                current_time,
                deliveries,
            )
            deliveries[delivery_id] = {
                "key": str(decision.get("key", "")).strip(),
                "dedupe_key": dedupe_key,
                "message": format_critical_sms(decision),
                "status": "pending",
                "attempts": 0,
                "created_at": current_text,
                "next_attempt_at": current_text,
            }
            enqueued += 1

        state["updated_at"] = current_text
        _write_state(state_path, state)

        due = []
        for delivery_id, record in deliveries.items():
            if not isinstance(record, dict) or record.get("status") != "pending":
                continue
            attempts = int(record.get("attempts", 0))
            next_attempt = _timestamp(record.get("next_attempt_at"))
            if attempts >= MAX_ATTEMPTS:
                record["status"] = "failed"
                record["last_error_code"] = "max_attempts"
                failed += 1
                continue
            if next_attempt is not None and next_attempt > current_time:
                continue
            due.append((delivery_id, record))

        due.sort(key=lambda item: str(item[1].get("created_at", "")))

        for delivery_id, record in due[:MAX_ATTEMPTS_PER_RUN]:
            attempted += 1
            record["attempts"] = int(record.get("attempts", 0)) + 1
            record["last_attempt_at"] = current_text
            _write_state(state_path, state)

            try:
                message_sid, provider_status = _send_twilio(
                    config,
                    str(record.get("message", "")),
                    client,
                )
            except CriticalSmsProviderError as exc:
                record["last_error_code"] = exc.code
                if exc.retryable and record["attempts"] < MAX_ATTEMPTS:
                    record["status"] = "pending"
                    record["next_attempt_at"] = _time_text(
                        current_time + RETRY_DELAY
                    )
                else:
                    record["status"] = "failed"
                    failed += 1
            else:
                record["status"] = "accepted"
                record["accepted_at"] = current_text
                record["provider_message_sid"] = message_sid
                record["provider_status"] = provider_status
                record.pop("last_error_code", None)
                accepted += 1

            state["updated_at"] = current_text
            _write_state(state_path, state)

        pending = sum(
            1
            for record in deliveries.values()
            if isinstance(record, dict) and record.get("status") == "pending"
        )
        state["updated_at"] = current_text
        _write_state(state_path, state)
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)

    if failed:
        status = "partial_failure"
    elif pending:
        status = "pending"
    elif accepted:
        status = "accepted"
    else:
        status = "idle"

    return {
        "enabled": True,
        "status": status,
        "eligible": len(selected),
        "enqueued": enqueued,
        "attempted": attempted,
        "accepted": accepted,
        "pending": pending,
        "failed": failed,
    }
