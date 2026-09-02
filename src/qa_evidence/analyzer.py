import hashlib
import json
import re
from collections import defaultdict

def _result_code(response):
    if isinstance(response, dict):
        for key in ("resultCode", "code", "errorCode", "statusCode"):
            if response.get(key) not in (None, ""):
                return str(response.get(key))
    return ""

def _message(response):
    if isinstance(response, dict):
        for key in (
            "resultDescription", "developerMessage", "message",
            "error", "errorMessage", "description"
        ):
            if response.get(key):
                return str(response.get(key))
    return ""

def _normalize_message(text):
    text = str(text or "").lower()
    text = re.sub(r"\b\d+\b", "#", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:300]

def error_fingerprint(entry):
    if not entry.has_error:
        return ""

    base = "|".join([
        entry.request_method.upper(),
        entry.request_uri,
        str(entry.response_status),
        _result_code(entry.response_body),
        entry.business_error_reason,
        _normalize_message(_message(entry.response_body)),
    ])
    digest = hashlib.sha1(base.encode("utf-8")).hexdigest()[:8].upper()
    return f"ERR-{digest}"

def find_duplicate_errors(entries):
    groups = defaultdict(list)
    for entry in entries:
        fp = error_fingerprint(entry)
        if fp:
            groups[fp].append(entry)
    return {fp: items for fp, items in groups.items() if len(items) > 1}

def build_auto_summary(entries):
    if not entries:
        return "No logs loaded."

    errors = [e for e in entries if e.is_error]
    business_errors = [e for e in entries if e.is_business_error]
    slow = [e for e in entries if e.is_slow]
    duplicate_groups = find_duplicate_errors(entries)
    txs = {e.transaction_id for e in entries if e.transaction_id}

    lines = [
        f"Observed {len(entries)} API logs across {len(txs)} transaction(s).",
        f"Detected {len(errors)} HTTP error(s), {len(business_errors)} business error(s), "
        f"and {len(slow)} slow API(s) (>= {entries[0].slow_threshold_ms:g} ms).",
    ]

    all_errors = [e for e in entries if e.has_error]
    if all_errors:
        first = all_errors[0]
        fp = error_fingerprint(first)
        lines.append(
            f"First error: {first.request_method or '-'} {first.request_uri or '-'} "
            f"returned {first.response_status or '-'} at {first.timestamp_display or '-'}"
            + (f" ({fp})." if fp else ".")
        )

    if duplicate_groups:
        duplicate_count = sum(len(v) for v in duplicate_groups.values())
        lines.append(
            f"Found {len(duplicate_groups)} repeated error signature(s) "
            f"covering {duplicate_count} error occurrences."
        )

    return " ".join(lines)

def transaction_journey(entries):
    ordered = sorted(entries, key=lambda entry: (
        entry.timestamp_sort or float("inf"), entry.index
    ))
    if not ordered:
        return None
    timed = [entry.timestamp_sort for entry in ordered if entry.timestamp_sort]
    duration_ms = (max(timed) - min(timed)) * 1000 if len(timed) >= 2 else 0.0
    numeric = []
    for entry in ordered:
        try:
            numeric.append((float(entry.response_time), entry))
        except (TypeError, ValueError):
            pass
    return {
        "entries": ordered,
        "first_api": ordered[0],
        "first_error": next((entry for entry in ordered if entry.has_error), None),
        "slowest_api": max(numeric, key=lambda pair: pair[0])[1] if numeric else None,
        "http_errors": sum(entry.is_error for entry in ordered),
        "business_errors": sum(entry.is_business_error for entry in ordered),
        "slow_count": sum(entry.is_slow for entry in ordered),
        "duration_ms": duration_ms,
        "uses_fallback": any(entry.transaction_is_fallback for entry in ordered),
    }
