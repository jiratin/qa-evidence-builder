import json
from .sanitizer import sanitize
from .analyzer import error_fingerprint, build_auto_summary

def _pretty(value, mask=True, extra_mask_keys=None):
    if mask:
        value = sanitize(value, extra_mask_keys)
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, indent=2)
    return str(value or "")

def build_ticket(
    entries,
    mask=True,
    expected="",
    actual="",
    extra_mask_keys=None,
    include_auto_summary=True,
):
    lines = ["QA DEFECT EVIDENCE", "=" * 76, ""]

    if not entries:
        return "\n".join(lines + ["No logs selected."])

    errors = sum(1 for e in entries if e.is_error)
    slow = sum(1 for e in entries if e.is_slow)
    transactions = sorted({e.transaction_id for e in entries if e.transaction_id})

    lines += [
        f"Selected logs: {len(entries)}",
        f"Errors (HTTP >= 400): {errors}",
        f"Slow APIs (>= 3000 ms): {slow}",
        f"Transactions: {len(transactions)}",
        "",
    ]

    if include_auto_summary:
        lines += [
            "AUTO SUMMARY",
            "-" * 76,
            build_auto_summary(entries),
            "",
        ]

    if expected.strip() or actual.strip():
        lines += [
            "EXPECTED RESULT",
            "-" * 76,
            expected.strip() or "-",
            "",
            "ACTUAL RESULT",
            "-" * 76,
            actual.strip() or "-",
            "",
        ]

    lines += ["TIMELINE", "-" * 76]

    for e in entries:
        flags = []
        if e.is_error:
            flags.append("ERROR")
        if e.is_slow:
            flags.append("SLOW")
        fp = error_fingerprint(e)
        if fp:
            flags.append(fp)
        flag_text = f" [{' | '.join(flags)}]" if flags else ""

        lines.append(
            f"{e.timestamp_display or '-'}  "
            f"{(e.request_method or '-'):6} "
            f"{e.request_uri or '-'}  "
            f"{e.response_status or '-'}  "
            f"{e.response_time or '-'} ms{flag_text}"
        )

    lines.append("")

    for n, e in enumerate(entries, start=1):
        flags = []
        if e.is_error:
            flags.append("ERROR")
        if e.is_slow:
            flags.append("SLOW")

        lines += [
            f"[API #{n}] {' | '.join(flags) if flags else 'OK'}",
            "-" * 76,
            f"Timestamp: {e.timestamp_display or '-'}",
            f"API: {e.request_method or '-'} {e.request_uri or '-'}",
            f"Status: {e.response_status or '-'}",
            f"Response Time: {e.response_time or '-'} ms",
            f"Request ID: {e.request_id or '-'}",
            f"Transaction ID: {e.transaction_id or '-'}",
            f"Error Fingerprint: {error_fingerprint(e) or '-'}",
            f"Page: {e.page_name or '-'}",
            f"Kafka Topic: {e.kafka_topic or '-'}",
            f"Source: {e.source_type}",
            "",
            "Query:",
            _pretty(e.query, mask, extra_mask_keys),
            "",
            "Request:",
            _pretty(e.request_body, mask, extra_mask_keys),
            "",
            "Response:",
            _pretty(e.response_body, mask, extra_mask_keys),
            "",
        ]

    return "\n".join(lines)

def build_markdown(
    entries,
    mask=True,
    expected="",
    actual="",
    extra_mask_keys=None,
):
    text = build_ticket(
        entries,
        mask,
        expected,
        actual,
        extra_mask_keys,
    )
    safe_text = text.replace("```", "[code-fence]")
    return "```text\n" + safe_text + "\n```\n"
