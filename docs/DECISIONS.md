# Project Decisions

These decisions capture constraints that are easy to lose between development
sessions. Change one only with an explicit requirement, tests, documentation,
changelog entry, and owner agreement where security or release scope expands.

## D-001 — Local-only processing

Imported logs may contain credentials, internal endpoints, and personal data.
The application has no upload, telemetry, or cloud-processing path. Future external
integrations require a separate security and authentication design.

## D-002 — Safe evidence defaults

Sensitive-data masking is enabled by default. Raw logs are disabled by default
and require confirmation because they bypass masking. Extra mask keys extend,
rather than replace, the default protected-key set.

## D-003 — Filtering and inclusion are different

A filter narrows investigation results but does not implicitly authorize export.
Only explicitly included logs enter copied or exported evidence. Inclusion can be
toggled through the indicator or Space when the timeline owns keyboard focus.

## D-004 — Transaction fallback remains visible

Transaction IDs resolve in the documented precedence order. Request ID is a useful
fallback but is not represented as an explicit transaction ID; its source and
fallback warning must remain visible in grouping and journey views.

## D-005 — Error Fingerprint is a grouping aid

The fingerprint deliberately groups repeated error shapes and is not a stable row
identifier, cryptographic proof, or cross-version compatibility promise. Numeric
message fragments are normalized to reduce per-instance noise. Changes to its
inputs can regroup historical evidence and therefore require tests and changelog.

## D-006 — PySide6 6.8.3 and Python 3.10–3.13

The Qt stack is pinned because a later packaging combination previously produced
a Windows executable that failed at startup. Dependency upgrades require building
and launching the packaged application; source imports alone are insufficient.
Python 3.14 is unsupported by the pinned runtime.

## D-007 — Native macOS artifacts

Apple Silicon and Intel applications are built separately and named explicitly.
Neither file may be described as universal unless its binary architectures are
actually validated as universal.

## D-008 — Release version is synchronized

The application, README, changelog, Windows metadata, workflow default, release
tests, and annotated Git tag use the same semantic version. Valid tags use
`vX.Y.Z`; the older dotted form `v.X.Y.Z` must not be repeated.

## D-009 — Constrained export templates

Custom root folder formats support only `{date}` and `{time}`. This keeps names
predictable and prevents arbitrary formatting fields or path traversal. Log file
formats support only `{date}`, `{time}`, `{millisecond}`, `{method}`, `{endpoint}`,
and `{short-id}`. Group and record filenames are sanitized independently and log
filenames remain capped at 80 characters.

## D-010 — Keep filters task-oriented

Filters are grouped by Search, Request, Result, Performance, and Context with
chips, presets, and per-category clear actions. A general-purpose rule builder is
deferred until user evidence justifies its complexity.

## D-011 — Synthetic repository samples only

Committed samples must not contain production/customer logs, valid credentials,
or personal data. Import issues and test fixtures should use synthetic values.

## D-012 — GitHub Actions is the release authority

Local builds help development, but publication depends on CI validation and
startup tests for Windows and both macOS architectures. Certificates and signing
secrets must never be guessed or committed.
