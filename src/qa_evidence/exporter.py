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
DEFAULT_EXPORT_LOG_FILENAME_FORMAT = "{date}_{time}_{millisecond}_{endpoint}"

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

def _log_timestamp_parts(entry):
    match = re.search(
        r"(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2}):(\d{2})(?:[.,](\d+))?",
        str(entry.timestamp_display or entry.timestamp_raw or ""),
    )
    if not match:
        return "unknown_date", "unknown_time", "000"
    year, month, day, hour, minute, second, fraction = match.groups()
    milliseconds = (fraction or "000")[:3].ljust(3, "0")
    return f"{year}{month}{day}", f"{hour}{minute}{second}", milliseconds

def _log_short_id(entry):
    identity = {
        "raw": entry.raw,
        "source_file": entry.source_file,
        "source_record_index": entry.source_record_index,
        "timestamp": entry.timestamp_raw,
    }
    encoded = json.dumps(identity, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:6].upper()

def build_export_log_filename(entry, template=DEFAULT_EXPORT_LOG_FILENAME_FORMAT):
    """Build one safe log filename from supported, non-sensitive tokens."""
    parsed = urlsplit(str(entry.request_uri or ""))
    basename = Path(parsed.path.rstrip("/")).name or "api"
    date, time, millisecond = _log_timestamp_parts(entry)
    method = _filename_token(str(entry.request_method or "UNKNOWN").upper(), "UNKNOWN", 10)
    short_id = _log_short_id(entry)
    values = {
        "date": date,
        "time": time,
        "millisecond": millisecond,
        "method": method,
        "endpoint": _filename_token(Path(basename).stem, "api"),
        "short-id": short_id,
    }
    try:
        rendered = str(template or DEFAULT_EXPORT_LOG_FILENAME_FORMAT).format(**values)
    except (AttributeError, IndexError, KeyError, ValueError) as exc:
        raise ValueError(
            "Export file format supports only {date}, {time}, {millisecond}, "
            "{method}, {endpoint}, and {short-id}."
        ) from exc
    if rendered.lower().endswith(".json"):
        rendered = rendered[:-5]
    stem = _filename_token(rendered, "log", MAX_EXPORT_LOG_FILENAME_LENGTH - 5)
    return f"{stem}.json"


def _log_filename(entry, template=DEFAULT_EXPORT_LOG_FILENAME_FORMAT):
    """Backward-compatible wrapper for exported log naming."""
    return build_export_log_filename(entry, template)

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


def _planned_filenames(entries, filename_format):
    """Return collision-free names without touching the filesystem."""
    used = set()
    names = []
    for entry in entries:
        filename = build_export_log_filename(entry, filename_format)
        candidate = filename
        sequence = 2
        while candidate in used:
            suffix = f"_{sequence}.json"
            candidate = f"{Path(filename).stem[:MAX_EXPORT_LOG_FILENAME_LENGTH - len(suffix)]}{suffix}"
            sequence += 1
        used.add(candidate)
        names.append(candidate)
    return names

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
        if mode == "page_url":
            page_folder = _safe(entry.page_url or "No Page URL")
            topic_folder = _safe(entry.kafka_topic or "No Kafka Topic")
            groups.setdefault(Path(page_folder) / topic_folder, []).append(entry)
            continue
        values = {"kafka": entry.kafka_topic, "page": entry.page_name, "page_url": entry.page_url}
        fallbacks = {"kafka": "No Kafka Topic", "page": "No Page Name", "page_url": "No Page URL"}
        value = values[mode]
        fallback = fallbacks[mode]
        groups.setdefault(_safe(value or fallback), []).append(entry)
    return groups


def build_export_structure(
    entries,
    root_name,
    mask=True,
    include_summary_txt=True,
    include_summary_md=True,
    include_raw=False,
    include_sanitized=True,
    group_by="none",
    custom_group_name="",
    include_zip=False,
    filename_format=DEFAULT_EXPORT_LOG_FILENAME_FORMAT,
):
    """Describe the exact package tree without writing files or log contents."""
    selected = list(entries)
    groups = _group_entries(selected, group_by, custom_group_name) if selected else {}
    selected_content_count = sum(bool(value) for value in (
        include_summary_txt, include_summary_md, include_raw, include_sanitized
    ))
    flatten_log_files = selected_content_count == 1
    grouped = str(group_by or "none").lower() != "none"
    group_items = []
    for folder_name, group in groups.items():
        group_path = tuple(Path(folder_name).parts) if grouped else ()
        files = []
        if include_summary_txt:
            files.append(("summary.txt",))
        if include_summary_md:
            files.append(("summary.md",))
        names = _planned_filenames(group, filename_format)
        if include_raw:
            prefix = () if flatten_log_files else ("raw",)
            files.extend(prefix + (name,) for name in names)
        if include_sanitized:
            prefix = () if flatten_log_files else ("sanitized",)
            files.extend(prefix + (name,) for name in names)
        group_items.append({"path": group_path, "count": len(group), "files": files})
    return {
        "root": _safe(root_name),
        "included_count": len(selected),
        "mask": bool(mask),
        "raw": bool(include_raw),
        "sanitized": bool(include_sanitized),
        "zip": bool(include_zip),
        "groups": group_items,
    }

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
    filename_format,
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
        name = build_export_log_filename(entry, filename_format)
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
    filename_format=DEFAULT_EXPORT_LOG_FILENAME_FORMAT,
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

    # Validate the template before creating any folder or file.
    build_export_log_filename(entries[0], filename_format)

    dest = Path(destination)
    groups = _group_entries(entries, group_by, custom_group_name)
    grouped = str(group_by or "none").lower() != "none"
    for folder_name, group in groups.items():
        target = dest / folder_name if grouped else dest
        _write_group(
            group, target, mask, expected, actual, extra_mask_keys,
            include_summary_txt, include_summary_md, include_raw, include_sanitized,
            filename_format,
        )

    if not include_zip:
        return dest

    zip_path = dest.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in dest.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(dest.parent))
    return zip_path
