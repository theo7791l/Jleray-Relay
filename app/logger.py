import time
from collections import deque
from dataclasses import dataclass, asdict
from typing import Deque
import asyncio

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

_logs: Deque[LogEntry] = deque(maxlen=MAX_LOGS)
_hits: dict = {}
_broadcast_callback = None

def set_broadcast_callback(cb):
    global _broadcast_callback
    _broadcast_callback = cb

def add_log(entry: LogEntry):
    _logs.appendleft(entry)
    _hits[entry.domain] = _hits.get(entry.domain, 0) + 1
    if _broadcast_callback:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(_broadcast_callback(asdict(entry)))
        except Exception:
            pass

def get_logs(limit: int = 50) -> list:
    return [asdict(e) for e in list(_logs)[:limit]]

def get_hits() -> dict:
    return dict(_hits)

def get_total_requests() -> int:
    return sum(_hits.values())
