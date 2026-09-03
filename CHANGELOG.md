# Changelog

All notable changes to QA Evidence Builder are documented in this file.

The project follows Semantic Versioning where practical.

## [Unreleased]

## [1.3.6] - 2026-09-04

### Added

- Display the application icon beside the in-app Sidebar brand.
- Show the current and total match count while searching the Evidence preview.

### Changed

- Name exported logs from their timestamp, method, endpoint, and a stable short
  hash, cap names at 80 characters for NAS compatibility, and preserve existing
  files by adding a numeric collision suffix.

### Fixed

- Resolve Kibana `CLIENT_PAGE_URL` fields and their `.keyword` variants before
  grouping exports by Page URL instead of placing those logs in `No Page URL`.

### Documentation

- Add page-specific UI contracts and context-efficient reading rules for future work.

## [1.3.5] - 2026-09-02

### Added

- Search the rendered Evidence preview with forward/backward navigation,
  wrap-around, keyboard actions, and optional case matching.

### Documentation

- Add project context, roadmap, architecture, decision records, and repository
  handoff rules; align repository and release instructions with the current build.

## [1.3.4] - 2026-09-02

### Added

- Default exports to `Log_{date}_{time}` and allow a safe custom folder-name format.
- Display the application icon in the GitHub README.

### Changed

- Add a collapsible filter panel, compact metric cards, user-resizable table columns,
  horizontal scrolling, higher-contrast Light Mode selection, and single-click/Space inclusion.

## [1.3.3] - 2026-09-02

### Added

- Detect business errors in HTTP-success responses using configurable success codes.
- Show transaction journey details, first failure, slowest API, duration, and fallback warnings.
- Add Unicode evidence notes to individual included logs.
- Import and merge multiple JSON/HAR files while retaining source filenames and record indexes.
- Persist a configurable slow-response threshold and use it across analysis and evidence.

### Fixed

- Create missing macOS bundle metadata keys safely and re-sign the bundle before launch validation.
- Group related search/filter controls, add removable active-filter chips,
  category clear actions and investigation presets, and consistently highlight alert/error text in red.

### Security

- Ignore local environment files, exported evidence folders, temporary files,
  additional tool caches, and profiling/benchmark output.
- Document that committed sample logs contain synthetic test data only.

## [1.3.2] - 2026-09-02

### Added

- Add branded Windows/macOS icon assets and `Guide Jir` application metadata.
- Show the source of each resolved Transaction ID and identify Request ID fallbacks.
- Report skipped records, unreadable timestamps, and missing endpoints after import.
- Warn inline and require confirmation before exporting unmasked raw logs.
- Validate release versions, required assets, artifact names, and macOS bundles.
- Launch-test both macOS packaged applications before publishing artifacts.

### Fixed

- Ignore malformed JSON/HAR records instead of aborting an entire import.
- Resolve transaction IDs from JSON request headers without case sensitivity.
- Keep the Help visibility regression check aligned with the PySide6 interface and run it in CI.

## [1.3.1] - 2026-09-01

### Fixed

- Pin the packaged Qt runtime to PySide6 6.8.3 to prevent the Windows executable from failing while importing QtCore.
- Launch-test the packaged Windows executable in GitHub Actions before publishing a release.

## [1.3.0] - 2026-09-01

### Added

- Parse, display, search, and export-group logs by `PAGE_URL`.

### Changed

- Exported log filenames now use a short endpoint and first-query-parameter format without special characters.
- A raw-only or sanitized-only export now places JSON files directly in the selected group folder.

### Fixed

- Explicitly style Qt dropdown popup text and selection colors in Light Mode.

## [1.2.0] - 2026-08-31

### Added

- Import support for a single JSON object in addition to JSON arrays and HAR.
- Export grouping by Kafka topic, page name, or a user-defined folder.
- Optional ZIP creation, disabled by default.
- Persistent Dark and Light themes.

### Changed

- Transaction ID resolution now prioritizes nested `transactionId`/`requestId` values in the request body, followed by URL/query parameters, then existing fields and headers.
- User Guide now matches the current PySide6 design and documents the complete import, grouping, theme, and export workflows.

## [1.1.1] - 2026-08-24

### Fixed

- Install the Linux EGL/XCB runtime libraries required by the headless PySide6 UI smoke test in GitHub Actions.

## [1.1.0] - 2026-08-24

### Changed

- Replaced the Tkinter interface with a custom-styled PySide6 dashboard.
- Added responsive sidebar navigation, summary cards, filter toolbar, timeline inspector, and dedicated transaction, evidence, and analysis workspaces.
- Preserved import, selection, filtering, masking, evidence, analysis, copy, and package export behavior.
- Updated local build scripts and GitHub Actions for the Qt runtime.
- Release descriptions are now generated from actual commits and pull requests, with categorized changes and stable download/security notes.


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
