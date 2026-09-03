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

Use synthetic test/sample logs only. Never commit credentials, customer logs,
local environment files, build output, exported evidence, or signing material.

Run the checks in `docs/RELEASING.md` before a release. Versions must be updated
in every location listed in `docs/PROJECT_CONTEXT.md`, and the annotated tag must
use `vX.Y.Z` and match the application version. Do not force-move published tags.

Preserve unrelated working-tree changes. Use Conventional Commit subjects and
do not commit or push unless the owner requests it.
