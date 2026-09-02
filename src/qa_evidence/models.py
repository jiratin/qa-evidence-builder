from dataclasses import dataclass, field
from typing import Any


DEFAULT_SUCCESS_CODES = ("0", "200", "20000", "SUCCESS", "OK")


def _nested_value(value, names):
    wanted = {name.casefold() for name in names}
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).casefold() in wanted:
                return item, str(key)
        for item in value.values():
            found, key = _nested_value(item, names)
            if key:
                return found, key
    elif isinstance(value, list):
        for item in value:
            found, key = _nested_value(item, names)
            if key:
                return found, key
    return None, ""

@dataclass
class LogEntry:
    index: int
    timestamp_raw: str = ""
    timestamp_display: str = ""
    timestamp_sort: float = 0.0
    request_uri: str = ""
    request_method: str = ""
    response_status: str = ""
    response_time: str = ""
    request_id: str = ""
    transaction_id: str = ""
    transaction_source: str = "not_found"
    transaction_source_field: str = ""
    transaction_is_fallback: bool = False
    page_name: str = ""
    page_url: str = ""
    kafka_topic: str = ""
    request_body: Any = ""
    response_body: Any = ""
    request_header: Any = ""
    query: Any = ""
    source_type: str = "json"
    source_file: str = ""
    source_record_index: int = 0
    note: str = ""
    slow_threshold_ms: float = 3000.0
    success_result_codes: tuple[str, ...] = DEFAULT_SUCCESS_CODES
    raw: dict = field(default_factory=dict)

    @property
    def is_error(self) -> bool:
        try:
            return int(self.response_status) >= 400
        except (TypeError, ValueError):
            return False

    @property
    def is_slow(self) -> bool:
        try:
            return float(self.response_time) >= self.slow_threshold_ms
        except (TypeError, ValueError):
            return False

    @property
    def business_error_reason(self) -> str:
        response = self.response_body
        success, success_field = _nested_value(response, ("success",))
        if success_field and (success is False or str(success).strip().casefold() in {"false", "0"}):
            return f"{success_field}=false"
        for field_name in ("errorCode", "errorMessage", "error"):
            error, error_field = _nested_value(response, (field_name,))
            if error_field and error not in (None, "", False, 0, "0"):
                return f"{error_field}={error}"
        result, result_field = _nested_value(response, ("resultCode",))
        if result_field and result not in (None, "") and str(result).strip().upper() not in {
            code.strip().upper() for code in self.success_result_codes
        }:
            return f"{result_field}={result}"
        return ""

    @property
    def is_business_error(self) -> bool:
        return bool(self.business_error_reason)

    @property
    def has_error(self) -> bool:
        return self.is_error or self.is_business_error

    @property
    def severity(self) -> str:
        if self.is_error:
            return "ERROR"
        if self.is_business_error:
            return "BUSINESS ERROR"
        if self.is_slow:
            return "SLOW"
        return "OK"


@dataclass
class ImportIssue:
    category: str
    message: str
    record_index: int | None = None


@dataclass
class ImportReport:
    source_format: str
    source_name: str = ""
    source_count: int = 0
    imported_count: int = 0
    skipped_count: int = 0
    invalid_timestamp_count: int = 0
    missing_endpoint_count: int = 0
    issues: list[ImportIssue] = field(default_factory=list)
    file_reports: list["ImportReport"] = field(default_factory=list)

    @property
    def warning_count(self) -> int:
        return self.invalid_timestamp_count + self.missing_endpoint_count


@dataclass
class ImportResult:
    entries: list[LogEntry]
    report: ImportReport
