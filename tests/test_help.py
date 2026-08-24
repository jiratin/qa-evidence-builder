import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from qa_evidence.help_content import HELP_SECTIONS

assert len(HELP_SECTIONS) >= 30
assert all(title.strip() for title, body in HELP_SECTIONS)
assert all(len(body.strip()) > 50 for title, body in HELP_SECTIONS)

combined = "\n".join(title + body for title, body in HELP_SECTIONS).lower()

for keyword in [
    "Import JSON / HAR",
    "Paste JSON",
    "Reset Filters",
    "Include Selected",
    "Exclude Selected",
    "Select All",
    "Deselect All",
    "Transactions",
    "Expected Result",
    "Actual Result",
    "Mask sensitive data",
    "Extra mask keys",
    "summary.txt",
    "summary.md",
    "Raw log files",
    "Sanitized log files",
    "Copy Included for Ticket",
    "Copy Included as Markdown",
    "Export Included Evidence",
    "Error Fingerprint",
    "Analysis",
    "Security",
]:
    assert keyword.lower() in combined, keyword

print("ALL_HELP_TESTS_PASSED")
