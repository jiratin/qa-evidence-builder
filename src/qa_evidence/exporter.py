import json
import re
import zipfile
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

from .evidence import build_ticket, build_markdown
from .sanitizer import sanitize

def _safe(s):
    s = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", str(s or "log")).strip(" .")
    return s[:120] or "log"

def _filename_token(value, fallback="log"):
    token = re.sub(r"[^A-Za-z0-9_-]+", "_", str(value or ""))
    token = re.sub(r"_+", "_", token).strip("_-")
    return token[:64] or fallback

def _log_filename(index, request_uri):
    """Create a short, stable filename from endpoint and first query pair."""
    parsed = urlsplit(str(request_uri or ""))
    basename = Path(parsed.path.rstrip("/")).name or "api"
    endpoint = _filename_token(Path(basename).stem, "api")
    parts = [f"{index:03d}", endpoint]
    query = parse_qsl(parsed.query, keep_blank_values=False)
    if query:
        key, value = query[0]
        parts.extend((_filename_token(key, "param"), _filename_token(value, "value")))
    return "_".join(parts) + ".json"

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

    for i, entry in enumerate(entries, start=1):
        name = _log_filename(i, entry.request_uri)
        if raw_dir:
            (raw_dir / name).write_text(
                json.dumps(entry.raw, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        if sanitized_dir:
            (sanitized_dir / name).write_text(
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
