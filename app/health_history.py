import time
from collections import defaultdict, deque
from typing import Dict, Deque

# Store last 60 data points per domain (1 per minute = 1h of history)
MAX_POINTS = 60

# {domain: deque([{"ts": float, "online": bool, "latency_ms": int}])}
_history: Dict[str, Deque[dict]] = defaultdict(lambda: deque(maxlen=MAX_POINTS))

def record(domain: str, online: bool, latency_ms: int):
    _history[domain].appendleft({
        "ts": time.time(),
        "online": online,
        "latency_ms": latency_ms if online else 0
    })

def get_history(domain: str) -> list:
    return list(_history[domain])

def get_uptime_percent(domain: str) -> float:
    h = list(_history[domain])
    if not h:
        return 0.0
    online_count = sum(1 for p in h if p["online"])
    return round(online_count / len(h) * 100, 1)

def get_avg_latency(domain: str) -> float:
    h = [p["latency_ms"] for p in _history[domain] if p["online"] and p["latency_ms"] > 0]
    return round(sum(h) / len(h), 1) if h else 0.0

def get_all_summaries() -> dict:
    result = {}
    for domain in _history:
        result[domain] = {
            "uptime": get_uptime_percent(domain),
            "avg_latency": get_avg_latency(domain),
            "points": len(_history[domain])
        }
    return result
