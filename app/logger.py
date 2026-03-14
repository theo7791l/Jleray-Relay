import json
import time
from collections import deque
from dataclasses import dataclass, asdict
from typing import Deque

MAX_LOGS = 200

@dataclass
class LogEntry:
    timestamp: float
    domain: str
    path: str
    method: str
    status: int
    backend: str
    duration_ms: int
    error: str = ""

# In-memory ring buffer (persists while server runs)
_logs: Deque[LogEntry] = deque(maxlen=MAX_LOGS)
_hits: dict = {}  # domain -> count

def add_log(entry: LogEntry):
    _logs.appendleft(entry)
    _hits[entry.domain] = _hits.get(entry.domain, 0) + 1

def get_logs(limit: int = 50) -> list:
    return [asdict(e) for e in list(_logs)[:limit]]

def get_hits() -> dict:
    return dict(_hits)

def get_total_requests() -> int:
    return sum(_hits.values())
