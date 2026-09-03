# Analysis Page

## Purpose

Classify HTTP, business, and slow failures; summarize the filtered result; and
group repeated errors using Error Fingerprints.

## Current UI and behaviour

- Persistent positive Slow threshold in milliseconds.
- Persistent comma-separated successful result codes.
- Auto defect summary for the current filtered records.
- Duplicate/similar error groups and occurrence details.
- Visible HTTP and Business Error alert counts.

## Classification contract

- HTTP error: numeric response status at least 400.
- Business error: supported `success`, error fields, or a `resultCode` outside
  configured successful codes.
- Slow: response time at least the configured threshold.
- Fingerprint is a grouping signature derived from method, URI, HTTP status,
  result code, business-error reason, and normalized message. It is not row ID.
- Analysis settings apply consistently to filters, Timeline flags, journeys,
  Preview, and exported summaries.

## Known roadmap boundary

Slow threshold and success codes are configurable. Arbitrary rule profiles and
configurable business-error field names are not implemented.

## Targeted implementation map

- UI: `_analysis_page`, `apply_analysis_settings`, and `update_analysis` in `app.py`.
- Record classification: `models.py`.
- Fingerprints, duplicate groups, summary, journey calculations: `analyzer.py`.
- Evidence representation: `evidence.py` only if output wording changes.
- Tests: classification, fingerprints, duplicates, thresholds, and summaries in
  `test_core.py`; widget/source assertions in UI tests.
- Requirements: FR-014–FR-018 and NFR-003a.

Read D-005 before changing fingerprint inputs. Read `TRANSACTIONS.md` when
journey calculations change and `DASHBOARD.md` when filter/severity display changes.
