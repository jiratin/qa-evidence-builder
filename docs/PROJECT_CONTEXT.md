# Project Context

This file provides the broad project baseline. For page-scoped work, start at
`pages/README.md` and read only the routed documents. Use this file when resuming
broad product work or preparing a handoff; do not load every project document by
default.

## Product direction

QA Evidence Builder is a local desktop application for QA engineers, testers,
and developers. It reduces the time required to locate related API logs, follow
a transaction journey, and produce sanitized evidence suitable for a defect or
technical investigation.

The product priorities are:

1. Protect sensitive log data and keep processing local.
2. Preserve reliable import, selection, masking, and evidence behaviour.
3. Make investigation faster without turning filters into a complex rule builder.
4. Support heterogeneous and increasingly large log sets.
5. Keep packaged Windows and macOS releases reproducible and launch-tested.

## Current baseline

- Current release: `v1.3.6`.
- Branch and release source: `main` at
  `https://github.com/jiratin/qa-evidence-builder`.
- UI: PySide6 desktop application.
- Supported Python: 3.10 through 3.13.
- Packaged Qt runtime: PySide6 6.8.3; do not upgrade without packaged startup tests.
- Publisher metadata: `Guide Jir`.
- Copyright: `Copyright © 2026 Guide Jir. All rights reserved.`
- Release targets: Windows, macOS Apple Silicon, and macOS Intel.

Released behaviour is defined by `REQUIREMENTS.md`, not by chat history. The
built-in searchable guide in `src/qa_evidence/help_content.py` is the user-facing
operating manual.

## Delivered through v1.3.6

- Single/multiple JSON and HAR import, merge, sorting, and source tracking.
- Page URL normalization across `PAGE_URL`, Kibana `CLIENT_PAGE_URL`, and HAR sources.
- Import validation counts for skipped and incomplete records.
- Transaction ID precedence, source display, and Request ID fallback warning.
- Timeline filtering, categorized collapsible filters, chips, presets, and clear actions.
- Single-click or Space inclusion, compact metrics, resizable columns, and horizontal scrolling.
- HTTP and business-error detection, error fingerprints, duplicate grouping, and transaction journey summary.
- Per-log evidence notes, Expected/Actual results, sanitized evidence, optional raw logs, and optional ZIP.
- Evidence Preview search with Next/Previous navigation and optional case matching.
- Grouped exports and configurable `Log_{date}_{time}` folder names.
- Chronological exported log filenames with stable non-sensitive short hashes.
- Dark/Light themes, branded icons, release metadata, and packaged startup validation.

See `ROADMAP.md` for partial and remaining work. In particular, do not assume
that Compare Two Logs, field-mapping profiles, export structure preview,
sensitive-data reports, workspace persistence, or large-file mode already exist.

## Non-negotiable compatibility constraints

- Processing remains local; do not upload imported logs or evidence.
- Sensitive-data masking is enabled by default.
- Raw-log export remains disabled by default and requires explicit confirmation.
- Malformed records must not discard usable records from the same import.
- Transaction fallback values must remain distinguishable from explicit IDs.
- A version tag must match every application and packaging version field.
- Windows and both macOS packages must launch successfully before publication.
- Sample logs committed to this repository must be synthetic.

## Continuation workflow

Before implementation:

1. Read the active roadmap item and its acceptance criteria.
2. Locate the matching requirement IDs and existing tests.
3. Check `DECISIONS.md` before changing dependencies, security, IDs, exports,
   fingerprints, or release behaviour.
4. Inspect the current working tree and preserve unrelated user changes.

For each completed user-visible change:

1. Implement the smallest coherent behaviour.
2. Add or update automated tests.
3. Update `REQUIREMENTS.md` and the built-in User Guide.
4. Update README for public capabilities and `CHANGELOG.md` under Unreleased.
5. Update roadmap status only after its acceptance criteria pass.
6. Run the checks documented in `RELEASING.md`.

## Definition of done

A roadmap item is Done only when implementation and regression tests pass, the
requirement and user guide agree with the UI, security implications have been
reviewed, and the changelog describes the user-visible result. A release is Done
only after CI builds and launch-tests all three packaged targets.

## Version and release checklist

For a release, update all version-bearing locations:

- `src/qa_evidence/__init__.py`
- `README.md`
- `CHANGELOG.md`
- `packaging/windows_version_info.txt`
- `.github/workflows/build-release.yml` workflow-dispatch default
- `tests/test_release_workflow.py`

Then follow `RELEASING.md`. Use an annotated `vX.Y.Z` tag and never move or
force-replace a published tag without explicit owner approval.

## Documentation ownership

- Page-level UI contracts and task routing: `pages/README.md`
- Current state and continuation rules: this file
- Planned scope and status: `ROADMAP.md`
- Behaviour contract: `REQUIREMENTS.md`
- Technical boundaries: `ARCHITECTURE.md`
- Reasons behind constraints: `DECISIONS.md`
- Release procedure: `RELEASING.md`
- User-facing history: `CHANGELOG.md`

When these documents disagree, verify the code and tests, correct the documents,
and record any intentional behavioural change in requirements and changelog.
