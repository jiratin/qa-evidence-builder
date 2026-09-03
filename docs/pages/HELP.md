# Help / User Guide

## Purpose

Provide searchable, in-app instructions that match the released UI and safety
behaviour without requiring external documentation.

## Current behaviour

- Help opens from the Sidebar and remains accessible across navigation pages.
- Sections are defined in `help_content.py` and rendered by `help_dialog.py`.
- User-visible controls, defaults, warnings, shortcuts, grouping, masking, and
  export behaviour must be documented when changed.

## Targeted implementation map

- Content: `src/qa_evidence/help_content.py`.
- Dialog/search/visibility: `src/qa_evidence/help_dialog.py`.
- Entry point: `open_help` and Sidebar construction in `app.py`.
- Tests: `tests/test_help.py` and `tests/test_help_visibility.py`; UI source test
  only when the Help entry point changes.
- Requirement: NFR-005 plus the requirement IDs for the feature being documented.

Do not read every Help section for a small update. Search for the affected
control or section title, edit that section, and add a focused keyword assertion
only when it protects important discoverability.
