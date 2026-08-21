# QA Evidence Builder — V3.1.1 0.3.1.1

Local-only desktop tool for converting API logs into ticket-ready QA evidence.

## Major V3 changes

### Explicit export selection
V3 no longer exports every currently filtered log by default.

In the Timeline:
1. Select one or more rows.
2. Click `Include Selected`.
3. Included rows display `☑` in the Export column.
4. Only included rows are used by:
   - Copy Included for Ticket
   - Copy Included as Markdown
   - Export Included Evidence

Other controls:
- Exclude Selected
- Include All Filtered
- Clear Included
- Double-click a Timeline row to toggle Include/Exclude

### Select package contents
Choose exactly what the ZIP contains:
- summary.txt
- summary.md
- Raw log files
- Sanitized log files

Raw logs are OFF by default.

### Responsive / dynamic UI
The previous single-screen layout has been replaced by:
- Scrollable left sidebar for controls/actions
- Main Notebook tabs:
  - Timeline
  - Transactions
  - Evidence
  - Analysis
- Timeline has horizontal/vertical scrollbars
- Sidebar remains usable at small window sizes by scrolling instead of hiding buttons
- Minimum supported window size is 840x560

### V3 analysis
- Error Fingerprint
- Duplicate/Similar error detection inside the current log set
- Auto Defect Summary
- Configurable additional masking keys

## Supported input
- Elasticsearch/Kibana-style JSON Array
- HAR

## Run on macOS

If Homebrew Python has no Tkinter:

    brew install python-tk@3.14

Then:

    python3 -m venv .venv
    source .venv/bin/activate
    python run.py

## Run on Windows

    py -m venv .venv
    .venv\Scripts\activate
    python run.py

## Test

    python tests/test_core.py

Expected:

    ALL_V3_TESTS_PASSED

## Build standalone

macOS:

    ./build_macos.command

Windows:

    build_windows.bat

## Security note

All analysis is local-only.

Sensitive-data masking is enabled by default. Raw log files are now excluded from
export by default and must be explicitly enabled in `Package Contents`.

Jira integration is intentionally not enabled in V3 because endpoint/auth/project
schema must be supplied by the organization before a safe implementation can be made.


## V3.1 — Help / User Guide

A new `Help / User Guide` button is available in the Source section.

The guide contains 30 beginner-friendly topics covering:
- Getting started
- JSON / HAR import
- Timeline
- Explicit export selection
- Every filter
- Transactions
- Expected / Actual
- Evidence Preview
- Masking and extra mask keys
- Package contents
- Copy / Markdown / Export
- Auto Defect Summary
- Error Fingerprint
- Duplicate error detection
- Example QA workflows
- Troubleshooting
- Security guidance
- Quick Start

The Help window is responsive:
- Resizable
- Minimum size protection
- Searchable
- Scrollable topic list
- Scrollable article content


## V3.1.1 Help visibility fix

The User Guide can now be opened from THREE places:

1. Persistent `Help / User Guide` button in the top-right header.
2. Application menu: `Help > User Guide`.
3. Sidebar: `Source > Help / User Guide`.

The header button stays visible independently of sidebar scrolling.

## V3.2
- Larger checkbox rows/click targets.
- Added Select All and Deselect All for log export selection.
- Help / User Guide moved to the bottom of the sidebar directly above the version label.
- Help menu remains as a secondary access path.
