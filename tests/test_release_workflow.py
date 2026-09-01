from pathlib import Path

root = Path(__file__).parents[1]
workflow = (root / ".github/workflows/build-release.yml").read_text(encoding="utf-8")
release_config = (root / ".github/release.yml").read_text(encoding="utf-8")

assert "releases/generate-notes" in workflow
assert "libegl1" in workflow
assert "libxkbcommon-x11-0" in workflow
assert "Launch-test Windows executable" in workflow
assert "Packaged executable exited during startup" in workflow
assert "--notes-file RELEASE_NOTES.md" in workflow
assert "> RELEASE_NOTES.md" in workflow
assert ">> RELEASE_NOTES.md" in workflow
assert "## Downloads" in workflow
assert "## Distribution notes" in workflow
assert "skip-changelog" in release_config
assert "New features" in release_config
assert 'labels:\n        - "*"' in release_config

print("ALL_RELEASE_WORKFLOW_TESTS_PASSED")
