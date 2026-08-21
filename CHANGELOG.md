# Changelog

All notable changes to QA Evidence Builder are documented in this file.

The project follows Semantic Versioning where practical.

## [1.0.0] - 2026-08-21

### Added

- Import Elasticsearch/Kibana-style JSON Array logs.
- Import HAR network logs.
- Paste JSON directly into the application.
- API Timeline with timestamp, method, endpoint, HTTP status, response time, Request ID, Transaction ID, and error fingerprint.
- Advanced filtering by:
  - Search text
  - HTTP method
  - HTTP status class
  - Minimum response time
  - Page name
  - Kafka topic
  - Transaction ID
  - Error-only
  - Slow-only
- Transaction grouping.
- Explicit log selection for evidence export.
- Include Selected / Exclude Selected.
- Select All / Deselect All.
- Expected Result / Actual Result fields.
- Ticket-ready evidence preview.
- Copy evidence as plain text.
- Copy evidence as Markdown.
- Sensitive-data masking.
- Custom additional mask keys.
- Selective Evidence Package contents:
  - summary.txt
  - summary.md
  - sanitized logs
  - raw logs
- Raw log export disabled by default.
- Error Fingerprint generation.
- Duplicate / similar error detection.
- Rule-based Auto Defect Summary.
- Built-in Help / User Guide.
- Responsive UI with scrollable sidebar and tabs.
- macOS and Windows build scripts.
- GitHub Actions automated builds for macOS and Windows.
- GitHub Release automation with downloadable macOS and Windows binaries.

### Changed

- macOS release artifacts are now split by CPU architecture.
- Added `QA-Evidence-Builder-macOS-Apple-Silicon.zip`.
- Added `QA-Evidence-Builder-macOS-Intel.zip`.
- Windows standalone executable remains `QA-Evidence-Builder-Windows.exe`.
- Release notes now explain which macOS build users should download.

### Security

- Application processing is local-only.
- Sensitive-data masking is enabled by default.
- Raw evidence export must be explicitly enabled.

### Distribution

GitHub Releases provide:

- `QA-Evidence-Builder-macOS.zip`
  - Contains `QA Evidence Builder.app`
- `QA-Evidence-Builder-Windows.exe`
  - Standalone Windows executable

### Known limitations

- macOS builds are not Apple Developer ID signed or notarized yet.
  Gatekeeper may warn users when opening downloaded builds.
- Windows builds are not Authenticode-signed yet.
  Microsoft Defender SmartScreen may show an unknown publisher warning.
- Jira integration is not included because organization-specific endpoint,
  authentication, project, and field mapping configuration is still required.
