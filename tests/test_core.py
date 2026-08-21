import sys
import tempfile
from pathlib import Path
import zipfile

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from qa_evidence.parser import parse_auto, parse_har
from qa_evidence.filtering import filter_entries, group_by_transaction
from qa_evidence.evidence import build_ticket, build_markdown
from qa_evidence.sanitizer import sanitize
from qa_evidence.exporter import export_package
from qa_evidence.analyzer import (
    error_fingerprint,
    find_duplicate_errors,
    build_auto_summary,
)

sample = [
    {
        "fields": {
            "TIMESTAMP": ["2026-08-21 11:03:36.230"],
            "REQUEST_URI": ["/api/v1/payment"],
            "REQUEST_METHOD": ["POST"],
            "RESPONSE_STATUS": [500],
            "RESPONSE_TIME": [3211],
            "REQUEST_ID": ["REQ-001"],
            "CLIENT_PAGE_NAME": ["Checkout"],
            "kafka_topic_name": ["payment-topic"],
            "REQUEST_BODY": ['{"password":"secret","customSecret":"value"}'],
            "RESPONSE_BODY": [
                '{"resultCode":"50001","resultDescription":"Internal Server Error"}'
            ],
            "REQUEST_HEADER": ['{"mfaf-transaction":"TX-001"}'],
        }
    },
    {
        "fields": {
            "TIMESTAMP": ["2026-08-21 11:03:37.000"],
            "REQUEST_URI": ["/api/v1/payment"],
            "REQUEST_METHOD": ["POST"],
            "RESPONSE_STATUS": [500],
            "RESPONSE_TIME": [3300],
            "REQUEST_ID": ["REQ-002"],
            "CLIENT_PAGE_NAME": ["Checkout"],
            "kafka_topic_name": ["payment-topic"],
            "REQUEST_BODY": ['{"password":"secret"}'],
            "RESPONSE_BODY": [
                '{"resultCode":"50001","resultDescription":"Internal Server Error"}'
            ],
            "REQUEST_HEADER": ['{"mfaf-transaction":"TX-001"}'],
        }
    },
    {
        "fields": {
            "TIMESTAMP": ["2026-08-21 11:03:38.000"],
            "REQUEST_URI": ["/api/v1/profile"],
            "REQUEST_METHOD": ["GET"],
            "RESPONSE_STATUS": [200],
            "RESPONSE_TIME": [120],
            "REQUEST_ID": ["REQ-003"],
            "CLIENT_PAGE_NAME": ["Profile"],
            "kafka_topic_name": ["profile-topic"],
            "REQUEST_BODY": ["{}"],
            "RESPONSE_BODY": ['{"resultCode":"20000"}'],
            "REQUEST_HEADER": ['{"mfaf-transaction":"TX-001"}'],
        }
    },
]

entries = parse_auto(sample)

assert len(entries) == 3
assert entries[0].transaction_id == "TX-001"
assert entries[0].is_error
assert entries[0].is_slow

errors = filter_entries(entries, errors_only=True)
assert len(errors) == 2

groups = group_by_transaction(entries)
assert len(groups["TX-001"]) == 3

fp1 = error_fingerprint(entries[0])
fp2 = error_fingerprint(entries[1])
assert fp1.startswith("ERR-")
assert fp1 == fp2

duplicates = find_duplicate_errors(entries)
assert fp1 in duplicates
assert len(duplicates[fp1]) == 2

summary = build_auto_summary(entries)
assert "Detected 2 HTTP error(s)" in summary
assert "repeated error signature" in summary

ticket = build_ticket(
    entries[:2],
    True,
    "Payment succeeds",
    "HTTP 500 returned",
    extra_mask_keys=["customSecret"],
)
assert "AUTO SUMMARY" in ticket
assert "Error Fingerprint:" in ticket
assert '"password": "********"' in ticket
assert '"customSecret": "********"' in ticket

markdown = build_markdown(entries[:1], True)
assert markdown.startswith("```text")

sanitized = sanitize(
    {
        "Authorization": "Bearer abc",
        "customSecret": "s1",
    },
    extra_keys=["customSecret"],
)
assert sanitized["Authorization"] == "********"
assert sanitized["customSecret"] == "********"

har = {
    "log": {
        "entries": [{
            "startedDateTime": "2026-08-21T04:03:36.230Z",
            "time": 450,
            "request": {
                "method": "GET",
                "url": "https://example.com/api/v1/config?x=1",
                "headers": [
                    {"name": "x-request-id", "value": "HAR-REQ-1"}
                ],
            },
            "response": {
                "status": 200,
                "content": {"text": '{"ok":true}'},
            },
        }]
    }
}

har_entries = parse_har(har)
assert len(har_entries) == 1
assert har_entries[0].request_uri == "/api/v1/config"

with tempfile.TemporaryDirectory() as directory:
    destination = Path(directory) / "evidence"

    archive_path = export_package(
        entries=entries[:1],
        destination=destination,
        include_summary_txt=True,
        include_summary_md=False,
        include_raw=False,
        include_sanitized=True,
    )

    assert archive_path.exists()

    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()

        assert any(name.endswith("summary.txt") for name in names)
        assert not any(name.endswith("summary.md") for name in names)
        assert not any("/raw/" in name for name in names)
        assert sum("/sanitized/" in name for name in names) == 1

print("ALL_V3_TESTS_PASSED")
