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

## Investigation

- FR-010: Display a filterable timeline and normalized log inspector.
- FR-011: Filter by search, method, status class, response time, page, Kafka
  topic, transaction, errors, and slow requests.
- FR-012: Include/exclude selected rows and include all filtered rows.
- FR-013: Group and navigate logs by Transaction ID.
- FR-014: Produce error fingerprints, automatic summaries, and duplicate groups.

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

## Application and delivery

- NFR-001: All log processing remains local; the application does not upload logs.
- NFR-002: Raw export remains disabled by default.
- NFR-003: The UI supports persistent Dark and Light modes and responsive navigation.
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

## Verification map

- Input, Transaction ID, masking, filtering, analysis, and export: `tests/test_core.py`
- UI availability, theme, and defaults: `tests/test_ui_smoke.py`
- UI framework/design source checks: `tests/test_ui_source.py`
- User Guide completeness: `tests/test_help.py`
- GitHub Release workflow: `tests/test_release_workflow.py`
