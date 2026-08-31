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
- FR-024: Export without grouping, by Kafka topic, by page name, or into a
  custom folder. Distinct Kafka/page values must produce distinct folders.
- FR-025: Create an evidence folder on every export. ZIP creation is optional
  and disabled by default.

## Application and delivery

- NFR-001: All log processing remains local; the application does not upload logs.
- NFR-002: Raw export remains disabled by default.
- NFR-003: The UI supports persistent Dark and Light modes and responsive navigation.
- NFR-004: Windows and macOS release builds are produced by GitHub Actions only
  after syntax, core, help, UI, and release-workflow checks pass.
- NFR-005: The searchable User Guide reflects the current UI and behaviour.

## Verification map

- Input, Transaction ID, masking, filtering, analysis, and export: `tests/test_core.py`
- UI availability, theme, and defaults: `tests/test_ui_smoke.py`
- UI framework/design source checks: `tests/test_ui_source.py`
- User Guide completeness: `tests/test_help.py`
- GitHub Release workflow: `tests/test_release_workflow.py`
