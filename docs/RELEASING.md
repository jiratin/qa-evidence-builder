# Release Guide

## Automatic release

The repository includes:

`.github/workflows/build-release.yml`

The workflow builds the application on both operating systems:

- macOS GitHub runner -> `QA Evidence Builder.app`
- Windows GitHub runner -> `QA-Evidence-Builder-Windows.exe`

It then creates or updates the matching GitHub Release.

## Normal release flow

Example for v1.0.1:

```bash
git add .
git commit -m "Release v1.0.1"
git push

git tag -a v1.0.1 -m "QA Evidence Builder v1.0.1"
git push origin v1.0.1
```

Pushing the tag triggers the GitHub Actions release workflow.

## Rebuild an existing tag manually

The workflow also supports `workflow_dispatch`.

On GitHub:

1. Open **Actions**.
2. Select **Build and Release**.
3. Click **Run workflow**.
4. Enter the existing release tag, such as `v1.0.0`.
5. Run the workflow.

This is useful for the current `v1.0.0` tag, because the tag may have existed
before this workflow was added.

## Release assets

The release contains:

### macOS

`QA-Evidence-Builder-macOS.zip`

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
