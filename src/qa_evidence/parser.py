import json
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs
from .models import LogEntry

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

def _preferred_identifier(value):
    return _find_nested(value, "transactionId") or _find_nested(value, "requestId")

def _parse_timestamp(value):
    if not value:
        return "", 0.0

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

def _transaction_id(fields):
    request_body = _first(fields, "REQUEST_BODY", "REQUEST_BODY.keyword")
    body_value = _preferred_identifier(request_body)
    if body_value:
        return str(body_value)

    request_uri = str(_first(fields, "REQUEST_URI", "REQUEST_URI.keyword"))
    parsed_uri = urlparse(request_uri)
    uri_query = parse_qs(parsed_uri.query)
    query_value = _preferred_identifier(uri_query)
    if query_value:
        return str(query_value[0] if isinstance(query_value, list) else query_value)

    request_params = _jsonish(_first(fields, "REQUEST_PARAMS", "REQUEST_PARAMS.keyword"))
    params_value = _preferred_identifier(request_params)
    if params_value:
        return str(params_value[0] if isinstance(params_value, list) else params_value)

    direct = _first(fields, "TRANSACTION_ID", "TRANSACTION_ID.keyword")
    if direct:
        return str(direct)

    header = _jsonish(_first(fields, "REQUEST_HEADER", "REQUEST_HEADER.keyword"))
    if isinstance(header, dict):
        for key in (
            "mfaf-transaction",
            "x-api-request-id",
            "x-request-id",
            "x-ssb-transaction-id",
        ):
            if header.get(key):
                return str(header[key])

    request_id = _first(fields, "REQUEST_ID", "REQUEST_ID.keyword")
    return str(request_id or "")

def parse_json_array(payload):
    if isinstance(payload, str):
        payload = json.loads(payload)
    if not isinstance(payload, list):
        raise ValueError("Input must be a JSON Array.")

    entries = []
    for i, raw in enumerate(payload, start=1):
        if not isinstance(raw, dict):
            continue

        fields = raw.get("fields") or raw.get("_source") or raw
        ts_raw = str(_first(fields, "TIMESTAMP", "TIMESTAMP.keyword", "@timestamp"))
        ts_display, ts_sort = _parse_timestamp(ts_raw)

        entries.append(LogEntry(
            index=i,
            timestamp_raw=ts_raw,
            timestamp_display=ts_display,
            timestamp_sort=ts_sort,
            request_uri=str(_first(fields, "REQUEST_URI", "REQUEST_URI.keyword")),
            request_method=str(_first(fields, "REQUEST_METHOD", "REQUEST_METHOD.keyword")),
            response_status=str(_first(fields, "RESPONSE_STATUS")),
            response_time=str(_first(fields, "RESPONSE_TIME")),
            request_id=str(_first(fields, "REQUEST_ID", "REQUEST_ID.keyword")),
            transaction_id=_transaction_id(fields),
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

    return sorted(entries, key=lambda e: (e.timestamp_sort or float("inf"), e.index))

def parse_har(payload):
    if isinstance(payload, str):
        payload = json.loads(payload)

    log = payload.get("log") if isinstance(payload, dict) else None
    if not isinstance(log, dict) or not isinstance(log.get("entries"), list):
        raise ValueError("Invalid HAR file.")

    out = []
    for i, item in enumerate(log["entries"], start=1):
        req = item.get("request") or {}
        res = item.get("response") or {}
        started = str(item.get("startedDateTime") or "")
        display, sort_value = _parse_timestamp(started)

        url = str(req.get("url") or "")
        parsed = urlparse(url)
        path = parsed.path or url
        query = parse_qs(parsed.query) if parsed.query else {}

        post_data = req.get("postData") or {}
        req_body = _jsonish(post_data.get("text", "")) if isinstance(post_data, dict) else ""

        content = res.get("content") or {}
        res_body = _jsonish(content.get("text", "")) if isinstance(content, dict) else ""

        headers = {
            str(h.get("name")): h.get("value")
            for h in req.get("headers", [])
            if isinstance(h, dict) and h.get("name")
        }
        headers_lower = {str(key).lower(): value for key, value in headers.items()}

        request_id = headers_lower.get("x-request-id") or headers_lower.get("x-api-request-id") or ""
        body_transaction = _preferred_identifier(req_body)
        query_transaction = _preferred_identifier(query)
        transaction_id = (
            body_transaction
            or (query_transaction[0] if isinstance(query_transaction, list) else query_transaction)
            or headers_lower.get("mfaf-transaction")
            or headers_lower.get("x-api-request-id")
            or request_id
        )

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
            page_url=str(headers_lower.get("referer") or item.get("pageref") or ""),
            request_body=req_body,
            response_body=res_body,
            request_header=headers,
            query=query,
            source_type="har",
            raw=item,
        ))

    return sorted(out, key=lambda e: (e.timestamp_sort or float("inf"), e.index))

def parse_auto(payload):
    parsed = json.loads(payload) if isinstance(payload, str) else payload
    if isinstance(parsed, list):
        return parse_json_array(parsed)
    if isinstance(parsed, dict) and isinstance(parsed.get("log"), dict):
        return parse_har(parsed)
    if isinstance(parsed, dict):
        return parse_json_array([parsed])
    raise ValueError("Unsupported input. Use a JSON object, JSON Array, or HAR.")
