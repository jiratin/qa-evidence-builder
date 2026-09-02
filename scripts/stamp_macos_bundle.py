"""Add deterministic application metadata to a PyInstaller macOS bundle."""

import argparse
import plistlib
from pathlib import Path
import re


ROOT = Path(__file__).parents[1]


def application_version() -> str:
    source = (ROOT / "src/qa_evidence/__init__.py").read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)', source)
    if not match:
        raise ValueError("Application version was not found.")
    return match.group(1)


def stamp(app: Path) -> Path:
    info_path = app / "Contents/Info.plist"
    if not info_path.is_file():
        raise ValueError(f"Info.plist was not found in {app}.")
    with info_path.open("rb") as stream:
        info = plistlib.load(stream)
    version = application_version()
    info.update({
        "CFBundleDisplayName": "QA Evidence Builder",
        "CFBundleGetInfoString": f"QA Evidence Builder {version}",
        "CFBundleIdentifier": "com.guidejir.qaevidencebuilder",
        "CFBundleName": "QA Evidence Builder",
        "CFBundleShortVersionString": version,
        "CFBundleVersion": version,
        "CFBundleIconFile": "qa-evidence-builder.icns",
        "NSHumanReadableCopyright": "Copyright © 2026 Guide Jir. All rights reserved.",
    })
    with info_path.open("wb") as stream:
        plistlib.dump(info, stream, sort_keys=True)
    return info_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("app", type=Path)
    args = parser.parse_args()
    print(stamp(args.app))
