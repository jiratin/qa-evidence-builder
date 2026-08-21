import json
import re
import zipfile
from pathlib import Path

from .evidence import build_ticket, build_markdown
from .sanitizer import sanitize

def _safe(s):
    s = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", str(s or "log")).strip(" .")
    return s[:120] or "log"

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
    dest.mkdir(parents=True, exist_ok=True)

    if include_summary_txt:
        (dest / "summary.txt").write_text(
            build_ticket(
                entries, mask, expected, actual, extra_mask_keys
            ),
            encoding="utf-8",
        )

    if include_summary_md:
        (dest / "summary.md").write_text(
            build_markdown(
                entries, mask, expected, actual, extra_mask_keys
            ),
            encoding="utf-8",
        )

    raw_dir = None
    sanitized_dir = None

    if include_raw:
        raw_dir = dest / "raw"
        raw_dir.mkdir(exist_ok=True)

    if include_sanitized:
        sanitized_dir = dest / "sanitized"
        sanitized_dir.mkdir(exist_ok=True)

    for i, e in enumerate(entries, start=1):
        api = _safe(e.request_uri.rstrip("/").split("/")[-1] or "api")
        name = f"{i:03d}_{api}.json"

        if raw_dir is not None:
            (raw_dir / name).write_text(
                json.dumps(e.raw, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        if sanitized_dir is not None:
            (sanitized_dir / name).write_text(
                json.dumps(
                    sanitize(e.raw, extra_mask_keys),
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

    zip_path = dest.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for p in dest.rglob("*"):
            if p.is_file():
                archive.write(p, p.relative_to(dest.parent))

    return zip_path
