# Release Guide

## Automatic release

The repository includes:

`.github/workflows/build-release.yml`

The workflow builds three native release artifacts:

- macOS Apple Silicon -> `QA-Evidence-Builder-macOS-Apple-Silicon.zip`
- macOS Intel -> `QA-Evidence-Builder-macOS-Intel.zip`
- Windows -> `QA-Evidence-Builder-Windows.exe`

It then creates or updates the matching GitHub Release. The description is
generated from the commits and pull requests since the previous tag, followed
by the project's download and security notes.

## Normal release flow

Replace `X.Y.Z` with the version being released:

```bash
git add .
git commit -m "feat: describe the user-visible change"
git push

python scripts/validate_release.py --tag vX.Y.Z --check-assets
git tag -a vX.Y.Z -m "QA Evidence Builder vX.Y.Z"
git push origin vX.Y.Z
```

Use tags in the form `v1.3.6`, not `v.1.3.6`. Pushing the tag triggers the
GitHub Actions release workflow. The tag must match `src/qa_evidence/__init__.py`,
the README version, Windows metadata, workflow-dispatch default, changelog, and
release-workflow test expectations.

## Release description

GitHub generates the `What's Changed` section automatically. Pull requests are
grouped using `.github/release.yml`; direct commits are also included in the
comparison. Use meaningful Conventional Commit subjects so the generated notes
remain useful:

```text
feat: add responsive evidence inspector
fix: preserve transaction filter after refresh
docs: update the release guide
ci: validate the PySide6 application before packaging
```

Add the `skip-changelog` label to a pull request only when it should be omitted
from public release notes. Re-running an existing release updates both its
assets and its generated description.

## Rebuild an existing tag manually

The workflow also supports `workflow_dispatch`.

On GitHub:

1. Open **Actions**.
2. Select **Build and Release**.
3. Click **Run workflow**.
4. Enter the exact existing release tag, such as `v1.3.6`.
5. Run the workflow.

Use this only to rebuild an existing tag. A new release should be triggered by
pushing a new annotated tag after the version and changelog have been updated.

## Release assets

The release contains:

### macOS

- `QA-Evidence-Builder-macOS-Apple-Silicon.zip`
- `QA-Evidence-Builder-macOS-Intel.zip`

After extraction:

`QA Evidence Builder.app`

A macOS `.app` is a bundle directory, so GitHub Release stores it inside a ZIP.

### Windows

`QA-Evidence-Builder-Windows.exe`

This is built with PyInstaller `--onefile --windowed`, so the user can run the
single `.exe` without installing Python or VS Code.

## Signing status

The CI workflow builds runnable binaries, but it does not currently sign them.

### macOS

For warning-free public distribution, add:

- Apple Developer Program account
- Developer ID Application certificate
- Code signing
- Apple notarization
- Stapling

### Windows

For stronger SmartScreen reputation and publisher verification, add an
Authenticode code-signing certificate.

These signing steps require private certificates/secrets and therefore should
not be guessed or committed to the repository.


## macOS architecture builds

The workflow now builds two separate macOS packages:

- `macos-latest` -> Apple Silicon build
- `macos-15-intel` -> Intel build

Release assets:

- `QA-Evidence-Builder-macOS-Apple-Silicon.zip`
- `QA-Evidence-Builder-macOS-Intel.zip`
- `QA-Evidence-Builder-Windows.exe`

Do not rename one macOS build to imply universal compatibility. These are separate native builds.

## Required checks before tagging

Run from the repository root with Python 3.10 through 3.13:

```bash
python -m compileall -q src run.py tests scripts
python scripts/validate_release.py --tag vX.Y.Z --check-assets
python tests/test_core.py
python tests/test_help.py
python tests/test_help_visibility.py
python tests/test_ui_source.py
python tests/test_ui_smoke.py
python tests/test_release_workflow.py
git diff --check
```

The packaged applications are launch-tested by CI. Local source checks do not
replace the Windows, Apple Silicon, and Intel packaging jobs.
