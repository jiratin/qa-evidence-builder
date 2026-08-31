import json
import re
import zipfile
from pathlib import Path

from .evidence import build_ticket, build_markdown
from .sanitizer import sanitize

def _safe(s):
    s = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", str(s or "log")).strip(" .")
    return s[:120] or "log"

def _group_entries(entries, group_by="none", custom_group_name=""):
    mode = str(group_by or "none").lower()
    if mode == "none":
        return {"": list(entries)}
    if mode == "custom":
        return {_safe(custom_group_name or "Selected Logs"): list(entries)}
    if mode not in {"kafka", "page"}:
        raise ValueError("Unsupported export grouping mode.")

    groups = {}
    for entry in entries:
        value = entry.kafka_topic if mode == "kafka" else entry.page_name
        fallback = "No Kafka Topic" if mode == "kafka" else "No Page Name"
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

    raw_dir = destination / "raw" if include_raw else None
    sanitized_dir = destination / "sanitized" if include_sanitized else None
    if raw_dir:
        raw_dir.mkdir(exist_ok=True)
    if sanitized_dir:
        sanitized_dir.mkdir(exist_ok=True)

    for i, entry in enumerate(entries, start=1):
        api = _safe(entry.request_uri.rstrip("/").split("/")[-1] or "api")
        name = f"{i:03d}_{api}.json"
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
