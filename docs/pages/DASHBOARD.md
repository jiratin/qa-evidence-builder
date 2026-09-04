# Dashboard Page

## Purpose

Investigate normalized logs, narrow results, inspect one record, and explicitly
choose which records enter Evidence.

## Current UI

- Compact metrics: Total logs, Successful, Errors, Slow APIs, and Included.
- Collapsible Search & Filters with task categories, active chips, presets,
  per-category Clear, and Reset count.
- Timeline columns: Export, Timestamp, Flag, Fingerprint, Method, API, Status,
  response time, Request ID, Transaction, plus user-selected fields found in the
  current JSON. Kafka Topic is selected by default.
- Resizable columns and horizontal scrolling. Timeline headers can be dragged
  into any order, and the order persists across application restarts.
- Timeline field selection persists locally; Dashboard filters never persist.
- Table headers, corners, empty areas, and scrollbars follow the active theme palette.
- The Timeline fields popup, selected rows, hover state, and checked indicators
  remain readable in both Light and Dark Mode.
- Log Inspector with normalized fields, raw payload view, alerts, and per-log note.

## Interaction contract

- Filtering and inclusion are separate states.
- Click the Export indicator once or press Space while Timeline owns focus to
  toggle inclusion. Space retains normal text-entry behaviour elsewhere.
- Select All includes the current filtered result; Deselect All clears inclusion.
- Presets are All Errors, Slow APIs, and Current Transaction.
- Filters combine using AND and refresh metrics, Timeline, Transactions,
  Evidence Preview, and Analysis.
- Page filtering searches both Page Name and normalized Page URL.

## Data and safety

- `LogEntry.index` is inclusion identity; Fingerprint is not row identity.
- Page URL may originate from `PAGE_URL`, `CLIENT_PAGE_URL`, aliases, or HAR.
- Request ID fallback must remain visibly distinct from an explicit Transaction ID.
- Notes belong to one `LogEntry` and enter output only when that log is included.

## Targeted implementation map

- UI: `_dashboard_page`, `_filters`, `_timeline_panel`, `_inspector_panel`,
  `refresh`, inclusion methods, `update_inspector`, and `save_log_note` in `app.py`.
- Filtering/grouping: `filtering.py`.
- Normalized fields: `models.py` and `parser.py`.
- Fingerprint/severity: `analyzer.py` and `models.py`.
- Tests: relevant Dashboard assertions in `test_ui_smoke.py`, `test_ui_source.py`,
  and parsing/filtering cases in `test_core.py`.
- Requirements: FR-005–FR-018 and NFR-003a–NFR-003e.

Read `TRANSACTIONS.md` if transaction grouping changes and `EVIDENCE.md` if
inclusion, notes, masking, preview, copy, or export semantics change.
