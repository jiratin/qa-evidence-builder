# Development Handoff Rules

## Context-efficient reading

Do not scan the whole repository or read every project document by default.
Before changing code:

1. Read `docs/pages/README.md` to route the task.
2. Read only the page document(s) that the request affects.
3. Follow only the source, test, requirement, and decision links listed in those
   page documents.
4. Search for the specific symbol or requirement ID before opening a large file.

Read `docs/PROJECT_CONTEXT.md` when resuming broad product work, checking the
current baseline, or preparing a handoff. Read `docs/ROADMAP.md` only for scope,
priority, or status decisions. Read `docs/ARCHITECTURE.md` when a change crosses
module boundaries. Read `docs/DECISIONS.md` only for the decision categories
relevant to the task. Read `docs/RELEASING.md` only for versioning, packaging,
CI, or release work.

A repository-wide scan is allowed case by case when the task is explicitly an
audit, the affected page/domain cannot be identified, a shared contract changes,
or evidence shows cross-cutting impact. State why the broader read is needed.

Treat `docs/REQUIREMENTS.md` as the released compatibility contract. Read the
relevant requirement section or IDs, not necessarily the entire file. Do not
silently remove or alter a requirement. Keep parsing, analysis, sanitization,
export, and UI orchestration within the boundaries in `docs/ARCHITECTURE.md`.

For every user-visible change:

- Add or update automated tests.
- Update the relevant requirement and built-in User Guide.
- Update README when public capabilities change.
- Add a concise entry under `CHANGELOG.md` Unreleased.
- Update roadmap status only after acceptance criteria pass.
- Preserve local-only processing, default masking, and raw-export confirmation.

For every new or changed UI component, verify both Light and Dark Mode. Check
the component's normal, hover, focus, selected, checked, disabled, popup, empty,
header/corner, and scrollbar states when applicable. Do not rely on the native
platform palette for a state that can fall back to an unreadable background or
text color. Add a targeted regression assertion for the relevant theme selector
or observable widget behavior.

Use synthetic test/sample logs only. Never commit credentials, customer logs,
local environment files, build output, exported evidence, or signing material.

Run the checks in `docs/RELEASING.md` before a release. Versions must be updated
in every location listed in `docs/PROJECT_CONTEXT.md`, and the annotated tag must
use `vX.Y.Z` and match the application version. Do not force-move published tags.

Preserve unrelated working-tree changes. Use Conventional Commit subjects and
do not commit or push unless the owner requests it.

## Response style

Reply in the user's dominant language. Keep exact technical terms, code,
commands, API names, error messages, paths, versions, and identifiers unchanged
unless the user asks for translation.

Default to concise, professional prose. Remove greetings, filler, repetition,
speculation, decorative emoji, and long raw logs. Never remove words such as
`not`, `never`, `no`, `only`, or `except` when doing so could change meaning.
Do not invent abbreviations merely to shorten a response.

Order project-work responses by relevance:

1. Outcome or current conclusion.
2. Important cause, risk, or decision, when present.
3. Files or behavior changed.
4. Verification performed and its result.
5. Remaining blocker or next action, only when one exists.

For status updates during longer work, state only what was learned, what is in
progress, or what needs attention. Do not repeat the full plan. Quote only the
shortest decisive part of an error unless more detail is requested.

Adapt response depth to the request:

- **Brief:** Direct answer or small completed change. One short paragraph or a
  compact list.
- **Standard:** Default for implementation, diagnosis, and review. Include the
  outcome, key evidence, verification, and any meaningful caveat.
- **Detailed:** Use when the user asks for explanation, acceptance criteria,
  handoff material, an audit, or when risk and sequencing require more context.

Clarity overrides brevity for security warnings, destructive or irreversible
actions, permission requests, release failures, and multi-step instructions
whose order matters. Persisted project artifacts such as code comments,
documentation, commit messages, release notes, and issue text must use normal,
complete professional language rather than compressed conversational phrasing.
