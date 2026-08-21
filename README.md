# QA Evidence Builder

QA Evidence Builder is a local desktop tool for QA, Testers, and Developers to turn API/network logs into focused evidence for defects, tickets, and technical investigation.

## Version

**v1.0.0**

## Key features

- Import Elasticsearch/Kibana-style JSON arrays
- Import HAR network logs
- Paste JSON directly into the application
- Timeline view with API, status, response time, request ID, transaction, and error fingerprint
- Search and filtering by method, status, page, Kafka topic, transaction, errors, and slow APIs
- Explicit log selection with Include/Exclude, Select All, and Deselect All
- Transaction grouping
- Expected Result / Actual Result evidence
- Sensitive-data masking and custom mask keys
- Plain-text and Markdown ticket evidence
- Selective evidence ZIP export
- Error fingerprinting and repeated-error analysis
- Built-in Help / User Guide
- Responsive/scrollable desktop UI

## Requirements

- Python 3
- Tkinter

On macOS with Homebrew Python 3.14, Tkinter can be installed with:

```bash
brew install python-tk@3.14
```

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python run.py
```

On Windows, activate the virtual environment with:

```powershell
.venv\Scripts\activate
python run.py
```

## Basic workflow

1. Import a JSON Array or HAR file.
2. Filter/search for relevant API logs.
3. Select the required rows.
4. Include selected logs, or use Select All for the current filtered result.
5. Review Evidence and optionally enter Expected/Actual results.
6. Keep sensitive-data masking enabled.
7. Copy the evidence for a ticket or export an evidence ZIP.

## Security

The application is designed to work locally. Logs may contain tokens, authorization headers, session identifiers, customer information, and other sensitive data. Review evidence before sharing it and prefer sanitized exports.

Raw log export is disabled by default.

## Tests

Core tests are located in `tests/`.

## Repository

GitHub: `jiratinteean/qa-evidence-builder`

## Release

Initial public release: **v1.0.0**

## Download ready-to-run builds

Prebuilt binaries are published under **GitHub Releases**.

### macOS

Choose the package that matches your Mac:

- **Apple Silicon (M1 / M2 / M3 / M4 and newer):** `QA-Evidence-Builder-macOS-Apple-Silicon.zip`
- **Intel Mac:** `QA-Evidence-Builder-macOS-Intel.zip`

Extract the ZIP, then open `QA Evidence Builder.app`.

### Windows

- Download `QA-Evidence-Builder-Windows.exe`
- Run the executable directly.

Users of these release builds do not need VS Code or a separate Python installation.

> macOS and Windows builds are currently unsigned. Gatekeeper or SmartScreen may display a warning until code signing is configured.
## Automated releases

GitHub Actions builds both operating-system versions whenever a version tag such as `v1.0.1` is pushed.

See [`docs/RELEASING.md`](docs/RELEASING.md) for the release process and manual rebuild instructions.

## Changelog

See [`CHANGELOG.md`](CHANGELOG.md).
