# Development Handoff Rules

Before changing this repository, read:

1. `docs/PROJECT_CONTEXT.md`
2. `docs/ROADMAP.md`
3. `docs/REQUIREMENTS.md`
4. `docs/ARCHITECTURE.md`
5. `docs/DECISIONS.md`

Treat `docs/REQUIREMENTS.md` as the released compatibility contract. Do not
silently remove or alter a requirement. Keep parsing, analysis, sanitization,
export, and UI orchestration within the module boundaries in `ARCHITECTURE.md`.

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
