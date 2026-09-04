import sys
import tempfile
import json
import re
from datetime import datetime
from pathlib import Path
import zipfile

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from qa_evidence.parser import merge_entries, parse_auto, parse_files, parse_har, parse_with_report
from qa_evidence.filtering import filter_entries, group_by_transaction
from qa_evidence.evidence import build_ticket, build_markdown
from qa_evidence.sanitizer import sanitize
from qa_evidence.exporter import (
    DEFAULT_EXPORT_LOG_FILENAME_FORMAT, MAX_EXPORT_LOG_FILENAME_LENGTH, _log_filename,
    build_export_folder_name, build_export_log_filename, build_export_structure,
    export_package,
)
from qa_evidence.analyzer import (
    error_fingerprint,
    find_duplicate_errors,
    build_auto_summary,
    transaction_journey,
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
assert entries[0].transaction_source == "request_header"
assert entries[0].transaction_source_field == "mfaf-transaction"
assert not entries[0].transaction_is_fallback
assert entries[0].is_error
assert entries[0].is_slow

single = parse_auto(sample[0])
assert len(single) == 1

body_transaction = parse_auto({"fields": {
    "REQUEST_URI": ["/api/fallback?transactionId=URI-TX"],
    "REQUEST_BODY": ['{"payload":{"requestId":"BODY-REQ","transactionId":"BODY-TX"}}'],
    "TRANSACTION_ID": ["FIELD-TX"],
}})
assert body_transaction[0].transaction_id == "BODY-TX"
assert body_transaction[0].transaction_source == "request_body"
assert body_transaction[0].transaction_source_field == "transactionId"

uri_transaction = parse_auto({"fields": {
    "REQUEST_URI": ["/api/v1/orders/query-transaction?transactionId=SERVICE260824152809-NE12816&orderId=123"],
    "REQUEST_BODY": ["{}"],
    "TRANSACTION_ID": ["FIELD-TX"],
}})
assert uri_transaction[0].transaction_id == "SERVICE260824152809-NE12816"
assert uri_transaction[0].transaction_source == "url_query"

case_insensitive_header = parse_auto({"fields": {
    "REQUEST_URI": ["/api/header-transaction"],
    "REQUEST_HEADER": ['{"X-Request-ID":"HEADER-REQ"}'],
}})
assert case_insensitive_header[0].transaction_id == "HEADER-REQ"
assert case_insensitive_header[0].transaction_source == "request_header"

fallback_transaction = parse_auto({"fields": {"REQUEST_ID": ["FALLBACK-REQ"]}})[0]
assert fallback_transaction.transaction_is_fallback
assert fallback_transaction.transaction_source == "request_id_fallback"

mixed_json_records = parse_auto([
    {"fields": ["invalid"]},
    {"fields": {"REQUEST_URI": ["/valid"]}},
    "invalid",
])
assert len(mixed_json_records) == 1
assert mixed_json_records[0].request_uri == "/valid"

mixed_result = parse_with_report([
    "invalid",
    {"fields": {"TIMESTAMP": ["not-a-time"]}},
    {"fields": {"TIMESTAMP": ["2026-08-21 11:03:36.230"], "REQUEST_URI": ["/ok"]}},
])
assert mixed_result.report.source_count == 3
assert mixed_result.report.imported_count == 2
assert mixed_result.report.skipped_count == 1
assert mixed_result.report.invalid_timestamp_count == 1
assert mixed_result.report.missing_endpoint_count == 1

existing_batch = parse_auto({"fields": {
    "TIMESTAMP": ["2026-08-21 11:03:40.000"], "REQUEST_URI": ["/existing"]
}})
existing_identity = existing_batch[0].index
added_batch = parse_auto({"fields": {
    "TIMESTAMP": ["2026-08-21 11:03:39.000"], "REQUEST_URI": ["/added"]
}})
merged_batches = merge_entries(existing_batch, added_batch)
assert [entry.request_uri for entry in merged_batches] == ["/added", "/existing"]
assert next(entry.index for entry in merged_batches if entry.request_uri == "/existing") == existing_identity
assert len({entry.index for entry in merged_batches}) == 2

page_url_entry = parse_auto({"fields": {
    "REQUEST_URI": ["/api/privateId.json"],
    "PAGE_URL": ["https://easyapp.example/orders/summary"],
}})[0]
assert page_url_entry.page_url == "https://easyapp.example/orders/summary"

kibana_page_url_entry = parse_auto({"fields": {
    "REQUEST_URI": ["/api/config/common"],
    "CLIENT_PAGE_URL": ["/demo/home"],
}})[0]
assert kibana_page_url_entry.page_url == "/demo/home"

kibana_sample_entries = parse_auto(
    (Path(__file__).parents[1] / "samples/qa_logs_72_entries_realistic.json").read_text(encoding="utf-8")
)
assert kibana_sample_entries
assert all(entry.page_url for entry in kibana_sample_entries)

filename_entry = parse_auto({"fields": {
    "TIMESTAMP": ["2026-09-03 10:29:03.111"],
    "REQUEST_METHOD": ["POST"],
    "REQUEST_URI": ["/api/privateId.json?commandId=2026090110091033335038"],
}})[0]
filename = _log_filename(filename_entry)
assert filename == "20260903_102903_111_privateId.json"
assert _log_filename(filename_entry) == filename
custom_filename = build_export_log_filename(
    filename_entry, "{method}_{endpoint}_{short-id}.json"
)
assert re.fullmatch(r"POST_privateId_[0-9A-F]{6}\.json", custom_filename)
assert DEFAULT_EXPORT_LOG_FILENAME_FORMAT == "{date}_{time}_{millisecond}_{endpoint}"
filename_entry.request_uri = "/api/" + ("veryLongEndpointName" * 10) + ".json"
long_filename = _log_filename(filename_entry)
assert len(long_filename) <= MAX_EXPORT_LOG_FILENAME_LENGTH
assert re.fullmatch(r"20260903_102903_111_[A-Za-z0-9_-]+\.json", long_filename)
filename_entry.request_uri = "/api/privateId.json?commandId=2026090110091033335038"
filename_entry.timestamp_raw = "not-a-time"
filename_entry.timestamp_display = "not-a-time"
assert _log_filename(filename_entry) == "unknown_date_unknown_time_000_privateId.json"
try:
    build_export_log_filename(filename_entry, "{request-id}")
except ValueError as exc:
    assert "supports only" in str(exc)
else:
    raise AssertionError("Unknown export-file tokens must be rejected")

export_moment = datetime(2026, 9, 2, 14, 5, 6)
assert build_export_folder_name(timestamp=export_moment) == "Log_20260902_140506"
assert build_export_folder_name("Evidence-{date}-{time}", export_moment) == "Evidence-20260902-140506"
assert "/" not in build_export_folder_name("../../Log_{date}", export_moment)
try:
    build_export_folder_name("Log_{unknown}", export_moment)
except ValueError as exc:
    assert "supports only" in str(exc)
else:
    raise AssertionError("Unknown export-folder tokens must be rejected")

preview_entry = parse_auto({"fields": {
    "TIMESTAMP": ["2026-09-03 10:29:03.111"],
    "REQUEST_URI": ["/api/preview"],
    "PAGE_URL": ["/orders"],
    "CLIENT_PAGE_NAME": ["Order<Page"],
    "kafka_topic_name": ["orders/topic"],
    "REQUEST_HEADER": ['{"Authorization":"must-not-appear"}'],
}})[0]
for preview_group in ("none", "kafka", "page", "page_url", "custom"):
    structure = build_export_structure(
        [preview_entry], "Log_20260903_102903", group_by=preview_group,
        custom_group_name="../../Custom", include_zip=True,
    )
    assert structure["root"] == "Log_20260903_102903"
    assert structure["included_count"] == 1
    assert structure["zip"]
    assert len(structure["groups"]) == 1
    assert structure["groups"][0]["count"] == 1
    assert ("summary.txt",) in structure["groups"][0]["files"]
    assert ("summary.md",) in structure["groups"][0]["files"]
    assert any(path[0] == "sanitized" for path in structure["groups"][0]["files"])
    assert structure["sanitized"] and not structure["raw"] and structure["mask"]
    assert "must-not-appear" not in repr(structure)
assert build_export_structure(
    [preview_entry], "root", group_by="page_url"
)["groups"][0]["path"] == ("_orders", "orders_topic")
assert build_export_structure(
    [preview_entry], "root", group_by="page"
)["groups"][0]["path"] == ("Order_Page",)
with tempfile.TemporaryDirectory() as directory:
    preview_destination = Path(directory) / "preview-must-not-exist"
    build_export_structure([preview_entry], preview_destination.name)
    assert not preview_destination.exists()

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

business_entry = parse_auto({"fields": {
    "TIMESTAMP": ["2026-08-21 11:03:39.000"],
    "REQUEST_URI": ["/api/business"],
    "RESPONSE_STATUS": [200],
    "RESPONSE_TIME": [2500],
    "RESPONSE_BODY": ['{"resultCode":"50001","resultDescription":"Invalid account"}'],
}})[0]
assert business_entry.is_business_error
assert business_entry.has_error
assert business_entry.severity == "BUSINESS ERROR"
assert error_fingerprint(business_entry).startswith("ERR-")
assert filter_entries([business_entry], business_errors_only=True) == [business_entry]
business_entry.success_result_codes = ("50001",)
assert not business_entry.is_business_error
business_entry.slow_threshold_ms = 2000
assert business_entry.is_slow
business_entry.slow_threshold_ms = 3000
assert not business_entry.is_slow

journey = transaction_journey(entries)
assert journey["first_api"] is entries[0]
assert journey["first_error"] is entries[0]
assert journey["slowest_api"] is entries[1]
assert journey["http_errors"] == 2
assert round(journey["duration_ms"]) == 1770

ticket = build_ticket(
    entries[:2],
    True,
    "Payment succeeds",
    "HTTP 500 returned",
    extra_mask_keys=["customSecret"],
)
assert "AUTO SUMMARY" in ticket
assert "Error Fingerprint:" in ticket
assert "Transaction Source:" in ticket
assert '"password": "********"' in ticket
assert '"customSecret": "********"' in ticket
entries[0].note = "จุดแรกที่เริ่มผิดพลาด"
entries[0].source_file = "payment.json"
ticket_with_note = build_ticket(entries[:1], True)
assert "จุดแรกที่เริ่มผิดพลาด" in ticket_with_note
assert "payment.json" in ticket_with_note

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
assert har_entries[0].transaction_source == "request_id_fallback"

malformed_har_entries = parse_har({"log": {"entries": [None, {
    "request": {"headers": "invalid"},
    "response": [],
}]}})
assert len(malformed_har_entries) == 1

with tempfile.TemporaryDirectory() as directory:
    first_file = Path(directory) / "first.json"
    second_file = Path(directory) / "second.har"
    broken_file = Path(directory) / "broken.json"
    first_file.write_text('[{"fields":{"TIMESTAMP":["2026-08-21 11:03:40.000"],"REQUEST_URI":["/later"]}}]', encoding="utf-8")
    second_file.write_text(json.dumps(har), encoding="utf-8")
    broken_file.write_text("not json", encoding="utf-8")
    multiple = parse_files([first_file, second_file, broken_file])
    assert len(multiple.entries) == 2
    assert multiple.entries[0].source_file == "second.har"
    assert multiple.entries[1].source_file == "first.json"
    assert [entry.index for entry in multiple.entries] == [1, 2]
    assert multiple.report.skipped_count == 1

with tempfile.TemporaryDirectory() as directory:
    destination = Path(directory) / "evidence"

    archive_path = export_package(
        entries=entries[:1],
        destination=destination,
        include_summary_txt=True,
        include_summary_md=False,
        include_raw=False,
        include_sanitized=True,
        include_zip=True,
    )

    assert archive_path.exists()

    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()

        assert any(name.endswith("summary.txt") for name in names)
        assert not any(name.endswith("summary.md") for name in names)
        assert not any("/raw/" in name for name in names)
        assert sum("/sanitized/" in name for name in names) == 1

with tempfile.TemporaryDirectory() as directory:
    invalid_destination = Path(directory) / "invalid-template"
    try:
        export_package(entries[:1], invalid_destination, filename_format="{secret}")
    except ValueError as exc:
        assert "supports only" in str(exc)
    else:
        raise AssertionError("Invalid filename format must stop export")
    assert not invalid_destination.exists()

with tempfile.TemporaryDirectory() as directory:
    grouped_entries = parse_auto([
        {"fields": {"REQUEST_URI": ["/a"], "kafka_topic_name": ["topic-a"]}},
        {"fields": {"REQUEST_URI": ["/b"], "kafka_topic_name": ["topic-b"]}},
        {"fields": {"REQUEST_URI": ["/c"], "kafka_topic_name": ["topic-a"]}},
        {"fields": {"REQUEST_URI": ["/d"], "kafka_topic_name": ["topic-c"]}},
    ])
    destination = Path(directory) / "grouped"
    result = export_package(
        grouped_entries, destination, group_by="kafka", include_zip=False
    )
    assert result == destination
    assert not destination.with_suffix(".zip").exists()
    assert (destination / "topic-a" / "summary.txt").exists()
    assert (destination / "topic-b" / "summary.txt").exists()
    assert (destination / "topic-c" / "summary.txt").exists()
    assert len(list((destination / "topic-a" / "sanitized").glob("*.json"))) == 2

with tempfile.TemporaryDirectory() as directory:
    destination = Path(directory) / "raw-only"
    export_package(
        entries[:1], destination,
        include_summary_txt=False,
        include_summary_md=False,
        include_raw=True,
        include_sanitized=False,
    )
    assert not (destination / "raw").exists()
    assert len(list(destination.glob("*.json"))) == 1

    export_package(
        entries[:1], destination,
        include_summary_txt=False,
        include_summary_md=False,
        include_raw=True,
        include_sanitized=False,
    )
    exported_names = sorted(path.name for path in destination.glob("*.json"))
    assert len(exported_names) == 2
    assert exported_names[1].endswith("_2.json")

with tempfile.TemporaryDirectory() as directory:
    destination = Path(directory) / "page-url-groups"
    page_entries = parse_auto([
        {"fields": {"REQUEST_URI": ["/a"], "PAGE_URL": ["/orders"], "kafka_topic_name": ["orders-topic"]}},
        {"fields": {"REQUEST_URI": ["/b"], "PAGE_URL": ["/profile"], "kafka_topic_name": ["profile-topic"]}},
    ])
    export_package(page_entries, destination, group_by="page_url")
    assert (destination / "_orders" / "orders-topic" / "summary.txt").exists()
    assert (destination / "_profile" / "profile-topic" / "summary.txt").exists()

with tempfile.TemporaryDirectory() as directory:
    destination = Path(directory) / "client-page-url-groups"
    page_entries = parse_auto([
        {"fields": {"REQUEST_URI": ["/a"], "CLIENT_PAGE_URL": ["/demo/home"]}},
        {"fields": {"REQUEST_URI": ["/b"], "CLIENT_PAGE_URL.keyword": ["/demo/profile"]}},
    ])
    export_package(page_entries, destination, group_by="page_url")
    assert (destination / "_demo_home" / "No Kafka Topic" / "summary.txt").exists()
    assert (destination / "_demo_profile" / "No Kafka Topic" / "summary.txt").exists()
    assert not (destination / "No Page URL").exists()

print("ALL_V3_TESTS_PASSED")
