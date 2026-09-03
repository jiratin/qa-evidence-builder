import hashlib
import json
import re
import zipfile
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

from .evidence import build_ticket, build_markdown
from .sanitizer import sanitize

MAX_EXPORT_LOG_FILENAME_LENGTH = 80

def _safe(s):
    s = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", str(s or "log")).strip(" .")
    return s[:120] or "log"

def build_export_folder_name(template="Log_{date}_{time}", timestamp=None):
    moment = timestamp or datetime.now()
    values = {"date": moment.strftime("%Y%m%d"), "time": moment.strftime("%H%M%S")}
    try:
        rendered = str(template or "Log_{date}_{time}").format(**values)
    except (AttributeError, IndexError, KeyError, ValueError) as exc:
        raise ValueError("Export folder format supports only {date} and {time}.") from exc
    return _safe(rendered)

def _filename_token(value, fallback="log", max_length=64):
    token = re.sub(r"[^A-Za-z0-9_-]+", "_", str(value or ""))
    token = re.sub(r"_+", "_", token).strip("_-")
    return token[:max_length] or fallback

def _log_timestamp_token(entry):
    match = re.search(
        r"(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2}):(\d{2})(?:[.,](\d+))?",
        str(entry.timestamp_display or entry.timestamp_raw or ""),
    )
    if not match:
        return "unknown_date_unknown_time_000"
    year, month, day, hour, minute, second, fraction = match.groups()
    milliseconds = (fraction or "000")[:3].ljust(3, "0")
    return f"{year}{month}{day}_{hour}{minute}{second}_{milliseconds}"

def _log_short_id(entry):
    identity = {
        "raw": entry.raw,
        "source_file": entry.source_file,
        "source_record_index": entry.source_record_index,
        "timestamp": entry.timestamp_raw,
    }
    encoded = json.dumps(identity, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:6].upper()

def _log_filename(entry):
    """Create a chronological, stable, non-sensitive filename for one log."""
    parsed = urlsplit(str(entry.request_uri or ""))
    basename = Path(parsed.path.rstrip("/")).name or "api"
    timestamp = _log_timestamp_token(entry)
    method = _filename_token(str(entry.request_method or "UNKNOWN").upper(), "UNKNOWN", 10)
    short_id = _log_short_id(entry)
    fixed_name = f"{timestamp}_{method}__{short_id}.json"
    endpoint_budget = max(8, MAX_EXPORT_LOG_FILENAME_LENGTH - len(fixed_name))
    endpoint = _filename_token(Path(basename).stem, "api", endpoint_budget)
    parts = [timestamp, method, endpoint, short_id]
    return "_".join(parts) + ".json"

def _available_path(directory, filename):
    candidate = directory / filename
    if not candidate.exists():
        return candidate
    stem, suffix = candidate.stem, candidate.suffix
    sequence = 2
    while (directory / f"{stem}_{sequence}{suffix}").exists():
        sequence += 1
    collision_suffix = f"_{sequence}{suffix}"
    trimmed_stem = stem[:MAX_EXPORT_LOG_FILENAME_LENGTH - len(collision_suffix)]
    return directory / f"{trimmed_stem}{collision_suffix}"

def _group_entries(entries, group_by="none", custom_group_name=""):
    mode = str(group_by or "none").lower()
    if mode == "none":
        return {"": list(entries)}
    if mode == "custom":
        return {_safe(custom_group_name or "Selected Logs"): list(entries)}
    if mode not in {"kafka", "page", "page_url"}:
        raise ValueError("Unsupported export grouping mode.")

    groups = {}
    for entry in entries:
        values = {"kafka": entry.kafka_topic, "page": entry.page_name, "page_url": entry.page_url}
        fallbacks = {"kafka": "No Kafka Topic", "page": "No Page Name", "page_url": "No Page URL"}
        value = values[mode]
        fallback = fallbacks[mode]
        groups.setdefault(_safe(value or fallback), []).append(entry)
    return groups

def _write_group(
    entries,
    destination,
    mask,
    expected,
    actual,
    extra_mask_keys,
    include_summary_txt,
    include_summary_md,
    include_raw,
    include_sanitized,
):
    destination.mkdir(parents=True, exist_ok=True)
    if include_summary_txt:
        (destination / "summary.txt").write_text(
            build_ticket(entries, mask, expected, actual, extra_mask_keys),
            encoding="utf-8",
        )
    if include_summary_md:
        (destination / "summary.md").write_text(
            build_markdown(entries, mask, expected, actual, extra_mask_keys),
            encoding="utf-8",
        )

    selected_content_count = sum(bool(value) for value in (
        include_summary_txt, include_summary_md, include_raw, include_sanitized
    ))
    flatten_log_files = selected_content_count == 1
    raw_dir = (destination if flatten_log_files else destination / "raw") if include_raw else None
    sanitized_dir = (destination if flatten_log_files else destination / "sanitized") if include_sanitized else None
    if raw_dir:
        raw_dir.mkdir(exist_ok=True)
    if sanitized_dir:
        sanitized_dir.mkdir(exist_ok=True)

    for entry in entries:
        name = _log_filename(entry)
        if raw_dir:
            _available_path(raw_dir, name).write_text(
                json.dumps(entry.raw, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        if sanitized_dir:
            _available_path(sanitized_dir, name).write_text(
                json.dumps(sanitize(entry.raw, extra_mask_keys), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

def export_package(
    entries,
    destination,
    mask=True,
    expected="",
    actual="",
    extra_mask_keys=None,
    include_summary_txt=True,
    include_summary_md=True,
    include_raw=False,
    include_sanitized=True,
    group_by="none",
    custom_group_name="",
    include_zip=False,
):
    if not entries:
        raise ValueError("No logs selected for export.")

    if not any([
        include_summary_txt,
        include_summary_md,
        include_raw,
        include_sanitized,
    ]):
        raise ValueError("Select at least one export content type.")

    dest = Path(destination)
    groups = _group_entries(entries, group_by, custom_group_name)
    grouped = str(group_by or "none").lower() != "none"
    for folder_name, group in groups.items():
        target = dest / folder_name if grouped else dest
        _write_group(
            group, target, mask, expected, actual, extra_mask_keys,
            include_summary_txt, include_summary_md, include_raw, include_sanitized,
        )

    if not include_zip:
        return dest

    zip_path = dest.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in dest.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(dest.parent))
    return zip_path
