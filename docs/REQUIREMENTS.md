# Product Requirements

This file is the compatibility contract for QA Evidence Builder. A change must
not remove or silently alter these behaviours without updating the requirement,
tests, User Guide, and changelog.

## Input

- FR-001: Import one Elasticsearch/Kibana-style JSON object.
- FR-002: Import a JSON array containing one or more log objects.
- FR-003: Import a valid HAR object.
- FR-004: Accept the same formats through Paste JSON.
- FR-005: Resolve Transaction ID from request body, URL/query, fields, headers,
  then Request ID fallback, in that order.
- FR-006: Report the source field used for every resolved Transaction ID and
  distinguish Request ID fallback values from explicit transaction values.
- FR-007: Report imported, skipped, invalid-timestamp, and missing-endpoint
  counts without exposing raw record contents. Mixed-validity input must retain
  usable records.
- FR-008: Import multiple JSON and HAR files in one operation, retain each
  source filename/record index, assign collision-free application indexes, and
  merge usable records in timestamp order.

## Investigation

- FR-010: Display a filterable timeline and normalized log inspector.
- FR-011: Filter by search, method, status class, response time, page, Kafka
  topic, transaction, errors, and slow requests.
- FR-012: Include/exclude selected rows and include all filtered rows.
- FR-013: Group and navigate logs by Transaction ID.
- FR-014: Produce error fingerprints, automatic summaries, and duplicate groups.
- FR-015: Detect business errors in successful HTTP responses from `success`,
  error fields, and configurable result-code conventions.
- FR-016: Provide a transaction journey summary with the first API, first
  error, slowest API, error counts, elapsed duration, and fallback warning.
- FR-017: Store an optional Unicode evidence note per log and include notes only
  when that log is included in copied or exported evidence.
- FR-018: Persist a positive slow-response threshold and success result-code
  list locally, applying them consistently to filters, analysis, and evidence.

## Evidence and export

- FR-020: Capture Expected and Actual results and show an exact preview.
- FR-021: Mask sensitive fields by default and accept extra mask keys.
- FR-022: Copy evidence as plain text or Markdown.
- FR-023: Select summary text, summary Markdown, raw, and sanitized contents.
- FR-024: Export without grouping, by Kafka topic, by page name, by page URL, or into a
  custom folder. Distinct Kafka/page values must produce distinct folders.
- FR-025: Create an evidence folder on every export. ZIP creation is optional
  and disabled by default.
- FR-026: Use filesystem-safe, concise exported filenames based on endpoint and
  the first query parameter. When raw or sanitized is the only selected content,
  place its JSON files directly in the current group folder.
- FR-027: Keep raw-log export disabled by default, show an inline warning when
  enabled, and require confirmation before the UI starts a raw export.
- FR-028: Default export folders to `Log_{date}_{time}` and allow a persisted,
  filesystem-safe custom format using only the `{date}` and `{time}` tokens.

## Application and delivery

- NFR-001: All log processing remains local; the application does not upload logs.
- NFR-002: Raw export remains disabled by default.
- NFR-003: The UI supports persistent Dark and Light modes and responsive navigation.
- NFR-003a: Search and filters are grouped by Search, Request, Result,
  Performance, and Context. Alert and error indicators use the shared danger
  text color in both themes.
- NFR-003b: Active filters are represented by individually removable chips,
  the reset action displays the active count, each category can be cleared,
  and presets cover all errors, slow APIs, and the selected transaction.
- NFR-003c: The filter panel is collapsible, dashboard metrics remain compact,
  and timeline/transaction columns are user-resizable with horizontal scrolling
  when their combined width exceeds the viewport.
- NFR-003d: Timeline inclusion toggles with one click on the Include indicator
  or Space while the table has focus; Space retains native behavior elsewhere.
- NFR-003e: Selected timeline text remains legible in both themes.
- NFR-004: Windows and macOS release builds are produced by GitHub Actions only
  after syntax, core, help, UI, and release-workflow checks pass.
- NFR-005: The searchable User Guide reflects the current UI and behaviour.
- NFR-006: PySide6 must remain pinned to the Windows packaging-tested version;
  dependency upgrades require launching the built executable in CI or locally.
  Supported source/build runtimes are Python 3.10 through 3.13.
- NFR-007: Source and packaged applications use the QA Evidence Builder icon,
  `Guide Jir` publisher metadata, and application version metadata.
- NFR-008: Release tags must match the application version. Required icons,
  artifact names, and macOS bundle contents are validated before publishing.
- NFR-009: Packaged Windows, macOS Apple Silicon, and macOS Intel applications
  must pass a startup test before their artifacts can be released.

## Behaviour clarifications

- Error Fingerprint is an error-grouping signature, not a permanent row ID. It
  is derived from method, URI, HTTP status, result code, business-error reason,
  and a normalized error message. Numeric message fragments are normalized so
  repeated instances of the same failure can group together.
- An empty or invalid export-folder format must never escape the chosen parent
  folder. Only `{date}` and `{time}` are supported; other format fields produce
  a user-visible validation error.
- The All Errors preset enables the error filter, Slow APIs enables the slow
  filter, and Current Transaction filters to the selected row's transaction.
- User preferences are local application settings. They contain UI preferences
  and analysis configuration, not imported log contents.

## Verification map

- Input, Transaction ID, masking, filtering, analysis, and export: `tests/test_core.py`
- UI availability, theme, and defaults: `tests/test_ui_smoke.py`
- UI framework/design source checks: `tests/test_ui_source.py`
- User Guide completeness: `tests/test_help.py`
- User Guide visibility and launch path: `tests/test_help_visibility.py`
- GitHub Release workflow, version metadata, and bundle stamping:
  `tests/test_release_workflow.py`
- Required icons, version/tag match, artifact names, and macOS bundles:
  `scripts/validate_release.py`

## Change acceptance

Every user-visible change must update the relevant requirement, automated test,
built-in User Guide, README when appropriate, and `CHANGELOG.md`. Before release,
all verification commands in `docs/RELEASING.md` and all three packaged startup
jobs must pass. Security-sensitive changes must preserve local-only processing,
default masking, and explicit raw-export confirmation.
