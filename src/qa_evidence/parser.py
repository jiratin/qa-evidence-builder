import json
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs
from .models import ImportIssue, ImportReport, ImportResult, LogEntry

def _first(fields, *names, default=""):
    for name in names:
        value = fields.get(name)
        if isinstance(value, list):
            if value:
                return value[0]
        elif value not in (None, ""):
            return value
    return default

def _jsonish(value):
    if not isinstance(value, str):
        return value
    text = value.strip()
    if not text:
        return ""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return value

def _find_nested(value, *names):
    """Find the first non-empty key recursively, case-insensitively."""
    value = _jsonish(value)
    wanted = {name.casefold() for name in names}
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).casefold() in wanted and item not in (None, "", [], {}):
                return item
        for item in value.values():
            found = _find_nested(item, *names)
            if found not in (None, "", [], {}):
                return found
    elif isinstance(value, list):
        for item in value:
            found = _find_nested(item, *names)
            if found not in (None, "", [], {}):
                return found
    return ""

def _find_nested_with_key(value, *names):
    value = _jsonish(value)
    wanted = {name.casefold() for name in names}
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).casefold() in wanted and item not in (None, "", [], {}):
                return item, str(key)
        for item in value.values():
            found, key = _find_nested_with_key(item, *names)
            if found not in (None, "", [], {}):
                return found, key
    elif isinstance(value, list):
        for item in value:
            found, key = _find_nested_with_key(item, *names)
            if found not in (None, "", [], {}):
                return found, key
    return "", ""

def _preferred_identifier(value):
    return _find_nested(value, "transactionId") or _find_nested(value, "requestId")

def _preferred_identifier_with_key(value):
    found, key = _find_nested_with_key(value, "transactionId")
    if found not in (None, "", [], {}):
        return found, key
    return _find_nested_with_key(value, "requestId")

def _parse_timestamp(value):
    if not value:
        return "", 0.0

    value = str(value)

    formats = (
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
    )
    for fmt in formats:
        try:
            dt = datetime.strptime(value, fmt)
            display = dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            return display, dt.replace(tzinfo=timezone.utc).timestamp()
        except ValueError:
            pass

    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], dt.timestamp()
    except Exception:
        return value, 0.0

def _transaction_details(fields):
    request_body = _first(fields, "REQUEST_BODY", "REQUEST_BODY.keyword")
    body_value, body_field = _preferred_identifier_with_key(request_body)
    if body_value:
        return str(body_value), "request_body", body_field, False

    request_uri = str(_first(fields, "REQUEST_URI", "REQUEST_URI.keyword"))
    parsed_uri = urlparse(request_uri)
    uri_query = parse_qs(parsed_uri.query)
    query_value, query_field = _preferred_identifier_with_key(uri_query)
    if query_value:
        value = query_value[0] if isinstance(query_value, list) else query_value
        return str(value), "url_query", query_field, False

    request_params = _jsonish(_first(fields, "REQUEST_PARAMS", "REQUEST_PARAMS.keyword"))
    params_value, params_field = _preferred_identifier_with_key(request_params)
    if params_value:
        value = params_value[0] if isinstance(params_value, list) else params_value
        return str(value), "request_params", params_field, False

    direct = _first(fields, "TRANSACTION_ID", "TRANSACTION_ID.keyword")
    if direct:
        return str(direct), "transaction_field", "TRANSACTION_ID", False

    header = _jsonish(_first(fields, "REQUEST_HEADER", "REQUEST_HEADER.keyword"))
    if isinstance(header, dict):
        normalized_headers = {str(key).casefold(): value for key, value in header.items()}
        for key in (
            "mfaf-transaction",
            "x-api-request-id",
            "x-request-id",
            "x-ssb-transaction-id",
        ):
            if normalized_headers.get(key):
                return str(normalized_headers[key]), "request_header", key, False

    request_id = _first(fields, "REQUEST_ID", "REQUEST_ID.keyword")
    if request_id:
        return str(request_id), "request_id_fallback", "REQUEST_ID", True
    return "", "not_found", "", False

def _transaction_id(fields):
    return _transaction_details(fields)[0]

def _parse_json_array_with_report(payload):
    if isinstance(payload, str):
        payload = json.loads(payload)
    if not isinstance(payload, list):
        raise ValueError("Input must be a JSON Array.")

    report = ImportReport(source_format="json", source_count=len(payload))
    entries = []
    for i, raw in enumerate(payload, start=1):
        if not isinstance(raw, dict):
            report.skipped_count += 1
            report.issues.append(ImportIssue("unsupported_record", "Record is not a JSON object.", i))
            continue

        fields = raw.get("fields") or raw.get("_source") or raw
        if not isinstance(fields, dict):
            report.skipped_count += 1
            report.issues.append(ImportIssue("invalid_fields", "fields/_source is not an object.", i))
            continue
        ts_raw = str(_first(fields, "TIMESTAMP", "TIMESTAMP.keyword", "@timestamp"))
        ts_display, ts_sort = _parse_timestamp(ts_raw)
        request_uri = str(_first(fields, "REQUEST_URI", "REQUEST_URI.keyword"))
        if not ts_raw or not ts_sort:
            report.invalid_timestamp_count += 1
            report.issues.append(ImportIssue("invalid_timestamp", "Timestamp is missing or could not be parsed.", i))
        if not request_uri:
            report.missing_endpoint_count += 1
            report.issues.append(ImportIssue("missing_endpoint", "Request endpoint is missing.", i))
        transaction_id, transaction_source, transaction_field, is_fallback = _transaction_details(fields)

        entries.append(LogEntry(
            index=i,
            timestamp_raw=ts_raw,
            timestamp_display=ts_display,
            timestamp_sort=ts_sort,
            request_uri=request_uri,
            request_method=str(_first(fields, "REQUEST_METHOD", "REQUEST_METHOD.keyword")),
            response_status=str(_first(fields, "RESPONSE_STATUS")),
            response_time=str(_first(fields, "RESPONSE_TIME")),
            request_id=str(_first(fields, "REQUEST_ID", "REQUEST_ID.keyword")),
            transaction_id=transaction_id,
            transaction_source=transaction_source,
            transaction_source_field=transaction_field,
            transaction_is_fallback=is_fallback,
            page_name=str(_first(fields, "CLIENT_PAGE_NAME", "CLIENT_PAGE_NAME.keyword")),
            page_url=str(_first(fields, "PAGE_URL", "PAGE_URL.keyword")),
            kafka_topic=str(_first(fields, "kafka_topic_name", "kafka_topic_name.keyword")),
            request_body=_jsonish(_first(fields, "REQUEST_BODY", "REQUEST_BODY.keyword")),
            response_body=_jsonish(_first(fields, "RESPONSE_BODY", "RESPONSE_BODY.keyword")),
            request_header=_jsonish(_first(fields, "REQUEST_HEADER", "REQUEST_HEADER.keyword")),
            query=_jsonish(_first(fields, "REQUEST_PARAMS", "REQUEST_PARAMS.keyword")),
            source_type="json",
            raw=raw,
        ))

    entries = sorted(entries, key=lambda e: (e.timestamp_sort or float("inf"), e.index))
    report.imported_count = len(entries)
    return ImportResult(entries, report)

def parse_json_array(payload):
    return _parse_json_array_with_report(payload).entries

def _parse_har_with_report(payload):
    if isinstance(payload, str):
        payload = json.loads(payload)

    log = payload.get("log") if isinstance(payload, dict) else None
    if not isinstance(log, dict) or not isinstance(log.get("entries"), list):
        raise ValueError("Invalid HAR file.")

    report = ImportReport(source_format="har", source_count=len(log["entries"]))
    out = []
    for i, item in enumerate(log["entries"], start=1):
        if not isinstance(item, dict):
            report.skipped_count += 1
            report.issues.append(ImportIssue("unsupported_record", "HAR entry is not an object.", i))
            continue
        req = item.get("request") or {}
        res = item.get("response") or {}
        if not isinstance(req, dict):
            req = {}
        if not isinstance(res, dict):
            res = {}
        started = str(item.get("startedDateTime") or "")
        display, sort_value = _parse_timestamp(started)
        if not started or not sort_value:
            report.invalid_timestamp_count += 1
            report.issues.append(ImportIssue("invalid_timestamp", "Timestamp is missing or could not be parsed.", i))

        url = str(req.get("url") or "")
        parsed = urlparse(url)
        path = parsed.path or url
        if not path:
            report.missing_endpoint_count += 1
            report.issues.append(ImportIssue("missing_endpoint", "Request endpoint is missing.", i))
        query = parse_qs(parsed.query) if parsed.query else {}

        post_data = req.get("postData") or {}
        req_body = _jsonish(post_data.get("text", "")) if isinstance(post_data, dict) else ""

        content = res.get("content") or {}
        res_body = _jsonish(content.get("text", "")) if isinstance(content, dict) else ""

        request_headers = req.get("headers", [])
        if not isinstance(request_headers, list):
            request_headers = []
        headers = {
            str(h.get("name")): h.get("value")
            for h in request_headers
            if isinstance(h, dict) and h.get("name")
        }
        headers_lower = {str(key).lower(): value for key, value in headers.items()}

        request_id = headers_lower.get("x-request-id") or headers_lower.get("x-api-request-id") or ""
        body_transaction, body_field = _preferred_identifier_with_key(req_body)
        query_transaction, query_field = _preferred_identifier_with_key(query)
        transaction_id = (
            body_transaction
            or (query_transaction[0] if isinstance(query_transaction, list) else query_transaction)
            or headers_lower.get("mfaf-transaction")
            or headers_lower.get("x-api-request-id")
            or request_id
        )
        if body_transaction:
            transaction_source, transaction_field, is_fallback = "request_body", body_field, False
        elif query_transaction:
            transaction_source, transaction_field, is_fallback = "url_query", query_field, False
        elif headers_lower.get("mfaf-transaction"):
            transaction_source, transaction_field, is_fallback = "request_header", "mfaf-transaction", False
        elif headers_lower.get("x-api-request-id"):
            transaction_source, transaction_field, is_fallback = "request_header", "x-api-request-id", False
        elif request_id:
            transaction_source, transaction_field, is_fallback = "request_id_fallback", "x-request-id", True
        else:
            transaction_source, transaction_field, is_fallback = "not_found", "", False

        out.append(LogEntry(
            index=i,
            timestamp_raw=started,
            timestamp_display=display,
            timestamp_sort=sort_value,
            request_uri=path,
            request_method=str(req.get("method") or ""),
            response_status=str(res.get("status") or ""),
            response_time=str(item.get("time") or ""),
            request_id=str(request_id),
            transaction_id=str(transaction_id),
            transaction_source=transaction_source,
            transaction_source_field=transaction_field,
            transaction_is_fallback=is_fallback,
            page_url=str(headers_lower.get("referer") or item.get("pageref") or ""),
            request_body=req_body,
            response_body=res_body,
            request_header=headers,
            query=query,
            source_type="har",
            raw=item,
        ))

    out = sorted(out, key=lambda e: (e.timestamp_sort or float("inf"), e.index))
    report.imported_count = len(out)
    return ImportResult(out, report)

def parse_har(payload):
    return _parse_har_with_report(payload).entries

def parse_auto(payload):
    return parse_with_report(payload).entries

def parse_with_report(payload):
    parsed = json.loads(payload) if isinstance(payload, str) else payload
    if isinstance(parsed, list):
        return _parse_json_array_with_report(parsed)
    if isinstance(parsed, dict) and isinstance(parsed.get("log"), dict):
        return _parse_har_with_report(parsed)
    if isinstance(parsed, dict):
        return _parse_json_array_with_report([parsed])
    raise ValueError("Unsupported input. Use a JSON object, JSON Array, or HAR.")
