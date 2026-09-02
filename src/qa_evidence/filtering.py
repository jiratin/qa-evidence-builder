def filter_entries(
    entries,
    search="",
    errors_only=False,
    business_errors_only=False,
    slow_only=False,
    method="ALL",
    status_class="ALL",
    min_ms="",
    page="",
    topic="",
    transaction="",
):
    q = (search or "").strip().lower()
    page_q = (page or "").strip().lower()
    topic_q = (topic or "").strip().lower()
    tx_q = (transaction or "").strip().lower()

    try:
        min_ms_value = float(min_ms) if str(min_ms).strip() else None
    except ValueError:
        min_ms_value = None

    out = []
    for e in entries:
        if errors_only and not e.has_error:
            continue
        if business_errors_only and not e.is_business_error:
            continue
        if slow_only and not e.is_slow:
            continue
        if method != "ALL" and e.request_method.upper() != method.upper():
            continue

        if status_class != "ALL":
            try:
                cls = f"{int(e.response_status) // 100}xx"
            except Exception:
                cls = "Other"
            if cls != status_class:
                continue

        if min_ms_value is not None:
            try:
                if float(e.response_time) < min_ms_value:
                    continue
            except Exception:
                continue

        haystack = " ".join([
            e.request_uri, e.request_id, e.transaction_id,
            e.page_name, e.page_url, e.kafka_topic, e.source_file,
            e.note, e.business_error_reason,
        ]).lower()

        if q and q not in haystack:
            continue
        if page_q and page_q not in f"{e.page_name} {e.page_url}".lower():
            continue
        if topic_q and topic_q not in e.kafka_topic.lower():
            continue
        if tx_q and tx_q not in e.transaction_id.lower():
            continue

        out.append(e)

    return out

def group_by_transaction(entries):
    groups = {}
    for e in entries:
        key = e.transaction_id or e.request_id or "(no transaction)"
        groups.setdefault(key, []).append(e)
    return groups
