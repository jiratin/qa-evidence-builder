# Evidence Page

## Purpose

Compose Expected/Actual results, inspect the exact masked evidence, search the
rendered Preview, copy ticket-ready text, and export a controlled local package.

## Current UI

- Expected Result and Actual Result editors.
- Tabbed preview area containing Included Evidence Preview and Export Tree Preview
  without increasing the page footprint.
- Expandable/collapsible export tree with exact root name, grouping folders,
  per-group counts, package files, masking/raw/sanitized state, and ZIP state.
- Preview tabs and their content panes use readable theme-specific backgrounds
  and text for normal, hover, selected, and disabled states.
- Preview search with Next, Previous, Enter, Shift+Enter, Match case,
  wrap-around, and `current / total matches` status.
- Mask sensitive data enabled by default and Extra mask keys.
- Package content controls for text, Markdown, raw, and sanitized logs.
- Grouping by none, Kafka topic, Page Name, Page URL, or custom folder.
- Configurable root format using `{date}` and `{time}`; optional ZIP.
- Configurable log filename format using `{date}`, `{time}`, `{millisecond}`,
  `{method}`, `{endpoint}`, and `{short-id}`.
- Copy for ticket, Copy as Markdown, and Export evidence actions.

## Export contract

- Only explicitly included records enter Preview, copy, or export.
- The Export Tree Preview is metadata-only and never writes folders/files or
  renders request/response contents.
- The preview root timestamp is retained for the next successful export so the
  folder name shown in the tree matches the folder that is created.
- Preview search never changes evidence contents or inclusion.
- Raw files are disabled by default, visibly warned, and confirmed before export.
- Page URL grouping uses the normalized `LogEntry.page_url` and nests a Kafka
  Topic folder beneath each Page URL folder. Missing values use `No Page URL`
  and `No Kafka Topic`.
- Exported log names default to `{date}_{time}_{millisecond}_{endpoint}.json`,
  support the documented custom tokens, and are capped at 80 characters. The
  optional short hash does not expose Request/Transaction IDs.
- Existing log files are not silently overwritten; collision suffixes are added.
- Sanitized-only or raw-only packages place JSON directly in the group folder.
- Export preferences persist locally, except masking always starts enabled and
  raw export always starts disabled.

## Targeted implementation map

- UI: `_evidence_page`, Preview-search methods, `update_preview`, copy methods,
  `_require_included`, and `export` in `app.py`.
- Rendering: `evidence.py`.
- Masking: `sanitizer.py`.
- Naming, grouping, structure preview, writing, ZIP: `exporter.py`.
- Page URL normalization: `parser.py` only when grouping input is wrong.
- Tests: evidence/export cases in `test_core.py`; Evidence widgets and search in
  `test_ui_smoke.py` and `test_ui_source.py`; instructions in `test_help.py`.
- Requirements: FR-017 and FR-020–FR-030; NFR-001, NFR-002, NFR-003e.

Read D-001, D-002, D-003, and D-009 before changing safety, inclusion, or paths.
