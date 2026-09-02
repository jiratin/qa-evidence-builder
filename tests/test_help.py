import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from qa_evidence.help_content import HELP_SECTIONS

assert len(HELP_SECTIONS) >= 30
assert all(title.strip() for title, body in HELP_SECTIONS)
assert all(len(body.strip()) > 50 for title, body in HELP_SECTIONS)

combined = "\n".join(title + body for title, body in HELP_SECTIONS)

for keyword in [
    "Import JSON / HAR",
    "Include Selected",
    "Transaction",
    "Expected Result",
    "Mask sensitive data",
    "Export evidence",
    "Error Fingerprint",
    "Security",
    "Single JSON",
    "Folder Grouping",
    "Dark / Light Mode",
    "Also create ZIP archive",
    "Find in Evidence Preview",
]:
    assert keyword.lower() in combined.lower(), keyword

print("ALL_HELP_TESTS_PASSED")
