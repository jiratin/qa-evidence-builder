# Application Shell

## Scope

Shared UI surrounding every main page: Sidebar branding/navigation, page title,
theme toggle, Import, Paste JSON, Clear, Export Evidence, status line, Help entry,
application icon, and responsive Sidebar width.

## Current behaviour

- Navigation pages are Dashboard, Transactions, Evidence, and Analysis.
- The Sidebar shows the packaged application icon, product name, local-only
  statement, version, and Help entry.
- Header actions remain available regardless of the active page.
- Import accepts one or more JSON/HAR files; Paste accepts supported JSON/HAR text.
- Clear removes loaded/included records, Expected/Actual text, and filters.
- Theme choice persists locally through `QSettings`.
- Import warnings report counts without showing complete raw records.

## Invariants

- Import and analysis remain local-only.
- Malformed records do not discard usable records from the same import.
- Shared actions must not behave differently merely because navigation changed.
- Application identity must remain consistent in-app and in packaged OS surfaces.

## Targeted implementation map

- UI/orchestration: `_build`, `_sidebar`, `_header`, `_navigate`, `resizeEvent`,
  `import_file`, `paste_json`, `_show_import_report`, and `clear_all` in `app.py`.
- Parsing: `parse_with_report` and `parse_files` in `parser.py`.
- Theme: `theme.py`.
- Help: `HELP.md`.
- Tests: `test_ui_smoke.py`, `test_ui_source.py`, `test_help_visibility.py`.
- Requirements: FR-001–FR-009 and NFR-001, NFR-003, NFR-005, NFR-007.

Read release documentation only if application metadata, bundled assets,
dependencies, or versions change.
