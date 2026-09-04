# Architecture

QA Evidence Builder is a local PySide6 desktop application. It intentionally has
no server component and no network integration.

## Data flow

```text
JSON / HAR / pasted JSON
        ↓
parse and normalize
        ↓
LogEntry records + ImportReport
        ↓
filter / group / analyze
        ↓
explicitly included records
        ↓
evidence rendering and sanitization
        ↓
clipboard or local export folder / optional ZIP
```

Filtering changes what the user investigates; inclusion controls what enters
evidence. These are separate states and must remain separate.

## Module boundaries

- `run.py`: source entry point and `src` path setup.
- `src/qa_evidence/app.py`: widgets, local UI state, user actions, and orchestration.
  Domain parsing, analysis, sanitization, and filename rules should not be added here.
- `models.py`: normalized records, import reports, and record-level classifications.
- `parser.py`: input detection, normalization, transaction resolution, issue reporting,
  multiple-source merge, and timestamp ordering.
- `filtering.py`: pure timeline filtering and transaction grouping.
- `analyzer.py`: error fingerprints, duplicate groups, summaries, and journeys.
- `evidence.py`: plain-text and Markdown evidence composition.
- `sanitizer.py`: recursive sensitive-key masking and extra-mask-key handling.
- `exporter.py`: safe names, grouping, package layout, JSON output, and optional ZIP.
- `theme.py`: shared Dark/Light style rules and semantic alert colors.
- `help_content.py` and `help_dialog.py`: searchable built-in user documentation.

## Core state

`LogEntry.index` is the collision-free application identity used for inclusion
and notes. `source_file` and `source_record_index` preserve provenance.
`transaction_id` may be explicit or a Request ID fallback; source fields and the
fallback flag must travel with the record.

Error Fingerprint is not row identity. It is an error grouping signature derived
from method, URI, status, result code, business-error reason, and normalized
message. Different rows can intentionally share a fingerprint.

## Local persistence

`QSettings` stores UI and analysis preferences including theme, filter-panel
visibility, slow threshold, successful result codes, selected Timeline fields,
extra mask-key rules, export grouping/package options, and folder/file formats.
Dashboard filter values, imported logs, evidence text, notes, and raw values are
not persisted there. Masking and raw-export defaults are restored safely on every
launch rather than inheriting an unsafe prior session state.

Future profile/workspace features must preserve that boundary unless their file
contents and security model are explicitly specified in requirements.

## Security boundaries

- Imported data stays in process and is written only by an explicit export action.
- Sanitized and raw exports are separate options.
- Raw export is opt-in and confirmed immediately before choosing/creating output.
- Filename and folder components are sanitized and must remain within the chosen parent.
- Error messages and import reports must not echo complete raw records or secrets.

## Delivery architecture

GitHub Actions runs Python 3.13 checks, then builds three targets independently:

- macOS Apple Silicon `.app` inside ZIP
- macOS Intel `.app` inside ZIP
- Windows one-file executable

Application metadata is stamped and validated before publication. Every packaged
binary is launched before its artifact can reach the release job. Local build
scripts are convenience tools; the GitHub workflow is the release authority.

## Testing layers

- `test_core.py`: domain behaviour and export safety.
- `test_ui_smoke.py`: live offscreen widget defaults and interaction smoke tests.
- `test_ui_source.py`: source-level UI regression guards.
- `test_help.py` and `test_help_visibility.py`: guide content and accessibility.
- `test_release_workflow.py`: CI, metadata, packaging, and release invariants.
- `validate_release.py`: version/tag, assets, artifact names, and macOS bundle validation.

Prefer pure functions and core tests for domain logic. Add UI tests when behaviour
depends on focus, signals, widget state, keyboard interaction, or theme rendering.
