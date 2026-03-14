import httpx
import asyncio
from typing import Dict

# Cache: backend_url -> {"online": bool, "latency_ms": int, "checked_at": float}
_status_cache: Dict[str, dict] = {}

async def check_backend(url: str) -> dict:
    import time
    start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url, follow_redirects=True)
        latency = int((time.monotonic() - start) * 1000)
        result = {"online": resp.status_code < 500, "latency_ms": latency, "checked_at": time.time()}
    except Exception as e:
        result = {"online": False, "latency_ms": -1, "checked_at": time.time(), "error": str(e)}
    _status_cache[url] = result
    return result

async def check_all(routes: dict) -> dict:
    tasks = {domain: check_backend(backend) for domain, backend in routes.items()}
    results = {}
    for domain, coro in tasks.items():
        results[domain] = await coro
    return results

def get_cached_status(url: str) -> dict:
    return _status_cache.get(url, {"online": None, "latency_ms": -1})
