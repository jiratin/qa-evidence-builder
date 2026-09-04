# Transactions Page

## Purpose

Group related API calls into a journey, expose the identifier source, identify
the first failure and slowest call, and include an entire journey in Evidence.

## Current UI and behaviour

- Table columns: Transaction ID, API count, HTTP errors, Business errors, Slow
  count, Duration, and Source.
- Selecting a group shows First API, First Error, Slowest API, duration, source
  warning, and calls ordered by timestamp.
- Double-clicking a transaction applies it to the Dashboard filter.
- Include journey adds every record in the selected group to Evidence.
- Request ID fallback grouping is explicitly marked as a warning.
- Table headers, corners, empty areas, and scrollbars follow the active theme palette.

## Invariants

- Journey order uses normalized timestamp and stable record order.
- Explicit transaction identifiers and Request ID fallback must not be conflated.
- Including a journey must not clear records already included elsewhere.
- Error and slow classifications use the current Analysis settings.

## Known roadmap boundary

Journey summary is delivered. Detection of missing or repeated expected calls is
still Partial because an expected journey/profile has not been defined. Do not
claim this behaviour exists.

## Targeted implementation map

- UI: `_transactions_page`, `apply_transaction_group`,
  `_selected_transaction_entries`, `include_transaction_journey`, and
  `update_journey_detail` in `app.py`.
- Grouping: `group_by_transaction` in `filtering.py`.
- Journey calculation: `transaction_journey` in `analyzer.py`.
- Transaction normalization: `_transaction_details` and HAR handling in `parser.py`.
- Tests: transaction and journey cases in `test_core.py`; widget assertions in
  `test_ui_smoke.py` and `test_ui_source.py`.
- Requirements: FR-005, FR-006, FR-013, FR-016, FR-018, and NFR-003c.

Read D-004 in `docs/DECISIONS.md` before changing transaction precedence or fallback.
