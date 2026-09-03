# Evidence Page

## Purpose

Compose Expected/Actual results, inspect the exact masked evidence, search the
rendered Preview, copy ticket-ready text, and export a controlled local package.

## Current UI

- Expected Result and Actual Result editors.
- Read-only Included Evidence Preview.
- Preview search with Next, Previous, Enter, Shift+Enter, Match case,
  wrap-around, and `current / total matches` status.
- Mask sensitive data enabled by default and Extra mask keys.
- Package content controls for text, Markdown, raw, and sanitized logs.
- Grouping by none, Kafka topic, Page Name, Page URL, or custom folder.
- Configurable root format using `{date}` and `{time}`; optional ZIP.
- Copy for ticket, Copy as Markdown, and Export evidence actions.

## Export contract

- Only explicitly included records enter Preview, copy, or export.
- Preview search never changes evidence contents or inclusion.
- Raw files are disabled by default, visibly warned, and confirmed before export.
- Page URL grouping uses the normalized `LogEntry.page_url`; missing values alone
  use `No Page URL`.
- Exported log names use
  `{date}_{time}_{millisecond}_{method}_{endpoint}_{short-id}.json`, are capped at
  80 characters, and do not expose Request/Transaction IDs through the short hash.
- Existing log files are not silently overwritten; collision suffixes are added.
- Sanitized-only or raw-only packages place JSON directly in the group folder.

## Known roadmap boundary

The textual Evidence Preview exists, but P0 Export Structure Preview remains
Partial: an exact pre-export folder tree with counts and package state has not
been implemented.

## Targeted implementation map

- UI: `_evidence_page`, Preview-search methods, `update_preview`, copy methods,
  `_require_included`, and `export` in `app.py`.
- Rendering: `evidence.py`.
- Masking: `sanitizer.py`.
- Naming, grouping, writing, ZIP: `exporter.py`.
- Page URL normalization: `parser.py` only when grouping input is wrong.
- Tests: evidence/export cases in `test_core.py`; Evidence widgets and search in
  `test_ui_smoke.py` and `test_ui_source.py`; instructions in `test_help.py`.
- Requirements: FR-017 and FR-020–FR-029; NFR-001, NFR-002, NFR-003e.

Read D-001, D-002, D-003, and D-009 before changing safety, inclusion, or paths.
