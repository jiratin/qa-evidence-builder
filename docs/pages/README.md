# Page Documentation Index

Use this index to select the minimum context needed for a task. Do not open all
page documents unless the change genuinely spans all pages.

## Task routing

| Task area | Read first | Common source |
|---|---|---|
| Sidebar, header, theme, import, paste, clear | `APPLICATION_SHELL.md` | `src/qa_evidence/app.py` |
| Metrics, filters, Timeline, Inspector, Include | `DASHBOARD.md` | `app.py`, `filtering.py`, `parser.py` |
| Transaction grouping and journey | `TRANSACTIONS.md` | `app.py`, `analyzer.py`, `filtering.py` |
| Expected/Actual, preview search, masking, copy, export | `EVIDENCE.md` | `app.py`, `evidence.py`, `sanitizer.py`, `exporter.py` |
| Business errors, thresholds, fingerprints, duplicates | `ANALYSIS.md` | `app.py`, `models.py`, `analyzer.py` |
| Help dialog or user instructions | `HELP.md` | `help_dialog.py`, `help_content.py` |

## Cross-cutting routing

- Input schema or normalization: relevant page document plus FR-001–FR-009.
- Evidence/export safety: `EVIDENCE.md` plus D-001, D-002, and D-009 in
  `docs/DECISIONS.md`.
- Transaction identity: `DASHBOARD.md` or `TRANSACTIONS.md` plus D-004.
- Fingerprint behaviour: `ANALYSIS.md` plus D-005.
- Dependency/runtime change: D-006 and `docs/ARCHITECTURE.md` Delivery architecture.
- Version, build, CI, tag, or release: `docs/RELEASING.md` and D-007, D-008, D-012.
- Priority or future scope: only the relevant phase in `docs/ROADMAP.md`.

## Reading rule

Search for named functions, widgets, or requirement IDs before reading full
source files. Broaden the inspection only when the task is an audit, affects a
shared data contract, crosses pages, or the initial targeted evidence is
insufficient. Preserve unrelated working-tree changes.
