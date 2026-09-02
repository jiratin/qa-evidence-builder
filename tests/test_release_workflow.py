from pathlib import Path
import plistlib
import sys
import tempfile

root = Path(__file__).parents[1]
sys.path.insert(0, str(root / "scripts"))
from stamp_macos_bundle import stamp
workflow = (root / ".github/workflows/build-release.yml").read_text(encoding="utf-8")
release_config = (root / ".github/release.yml").read_text(encoding="utf-8")
stamp_source = (root / "scripts/stamp_macos_bundle.py").read_text(encoding="utf-8")

assert "releases/generate-notes" in workflow
assert "libegl1" in workflow
assert "libxkbcommon-x11-0" in workflow
assert "Launch-test Windows executable" in workflow
assert "Packaged executable exited during startup" in workflow
assert workflow.count("Validate and launch-test packaged application") == 2
assert "scripts/validate_release.py" in workflow
assert "qa-evidence-builder.icns" in workflow
assert "qa-evidence-builder.ico" in workflow
assert "windows_version_info.txt" in workflow
assert "Guide Jir" in stamp_source
assert workflow.count("scripts/stamp_macos_bundle.py") == 2
assert workflow.count("codesign --force --deep --sign -") == 2
assert "PlistBuddy" not in workflow
assert "python tests/test_help_visibility.py" in workflow
assert "--notes-file RELEASE_NOTES.md" in workflow
assert "> RELEASE_NOTES.md" in workflow
assert ">> RELEASE_NOTES.md" in workflow
assert "## Downloads" in workflow
assert "## Distribution notes" in workflow
assert "skip-changelog" in release_config
assert "New features" in release_config
assert 'labels:\n        - "*"' in release_config

with tempfile.TemporaryDirectory() as directory:
    app = Path(directory) / "QA Evidence Builder.app"
    contents = app / "Contents"
    contents.mkdir(parents=True)
    with (contents / "Info.plist").open("wb") as stream:
        plistlib.dump({"CFBundleName": "QA Evidence Builder"}, stream)
    stamp(app)
    with (contents / "Info.plist").open("rb") as stream:
        info = plistlib.load(stream)
    assert info["CFBundleVersion"] == "1.3.3"
    assert info["CFBundleShortVersionString"] == "1.3.3"
    assert info["CFBundleIconFile"] == "qa-evidence-builder.icns"
    assert "Guide Jir" in info["NSHumanReadableCopyright"]

print("ALL_RELEASE_WORKFLOW_TESTS_PASSED")
