"""Validate source assets, version consistency, and packaged release structure."""

import argparse
import plistlib
from pathlib import Path
import re
import sys


ROOT = Path(__file__).parents[1]
EXPECTED_ARTIFACTS = {
    "QA-Evidence-Builder-Windows.exe",
    "QA-Evidence-Builder-macOS-Apple-Silicon.zip",
    "QA-Evidence-Builder-macOS-Intel.zip",
}


def application_version() -> str:
    source = (ROOT / "src/qa_evidence/__init__.py").read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)', source)
    if not match:
        raise ValueError("Application version was not found.")
    return match.group(1)


def validate_version(tag: str) -> None:
    normalized = str(tag).removeprefix("v")
    if normalized != application_version():
        raise ValueError(f"Release version {tag} does not match application version {application_version()}.")


def validate_assets() -> None:
    required = (
        ROOT / "assets/icons/qa-evidence-builder.ico",
        ROOT / "assets/icons/qa-evidence-builder.icns",
        ROOT / "assets/icons/png/icon-256.png",
        ROOT / "packaging/windows_version_info.txt",
    )
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file() or path.stat().st_size == 0]
    if missing:
        raise ValueError("Missing required release assets: " + ", ".join(missing))
    metadata = (ROOT / "packaging/windows_version_info.txt").read_text(encoding="utf-8")
    if f"StringStruct('ProductVersion', '{application_version()}')" not in metadata:
        raise ValueError("Windows ProductVersion does not match the application version.")
    if "Guide Jir" not in metadata:
        raise ValueError("Windows publisher metadata is missing.")


def validate_macos_app(app: Path) -> None:
    info_path = app / "Contents/Info.plist"
    executable = app / "Contents/MacOS/QA Evidence Builder"
    icon = app / "Contents/Resources/qa-evidence-builder.icns"
    if not all(path.is_file() and path.stat().st_size for path in (info_path, executable, icon)):
        raise ValueError("macOS application is missing its Info.plist, executable, or icon.")
    with info_path.open("rb") as stream:
        info = plistlib.load(stream)
    expected = application_version()
    if info.get("CFBundleShortVersionString") != expected:
        raise ValueError("macOS bundle version does not match the application version.")
    if info.get("CFBundleIconFile") not in {"qa-evidence-builder.icns", "qa-evidence-builder"}:
        raise ValueError("macOS bundle does not reference the application icon.")


def validate_artifacts(directory: Path) -> None:
    existing = {path.name for path in directory.iterdir() if path.is_file() and path.stat().st_size}
    missing = EXPECTED_ARTIFACTS - existing
    if missing:
        raise ValueError("Missing release artifacts: " + ", ".join(sorted(missing)))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag")
    parser.add_argument("--check-assets", action="store_true")
    parser.add_argument("--macos-app", type=Path)
    parser.add_argument("--artifacts", type=Path)
    args = parser.parse_args()
    try:
        if args.tag:
            validate_version(args.tag)
        if args.check_assets:
            validate_assets()
        if args.macos_app:
            validate_macos_app(args.macos_app)
        if args.artifacts:
            validate_artifacts(args.artifacts)
    except (OSError, ValueError) as exc:
        print(f"RELEASE_VALIDATION_FAILED: {exc}", file=sys.stderr)
        return 1
    print("RELEASE_VALIDATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
