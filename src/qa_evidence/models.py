from dataclasses import dataclass, field
from typing import Any

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
    page_name: str = ""
    kafka_topic: str = ""
    request_body: Any = ""
    response_body: Any = ""
    request_header: Any = ""
    query: Any = ""
    source_type: str = "json"
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
            return float(self.response_time) >= 3000
        except (TypeError, ValueError):
            return False

    @property
    def severity(self) -> str:
        if self.is_error:
            return "ERROR"
        if self.is_slow:
            return "SLOW"
        return "OK"
