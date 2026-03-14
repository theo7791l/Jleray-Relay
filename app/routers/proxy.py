from fastapi import Request
from fastapi.responses import Response, HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx
import time
from app.config import load_config
from app.logger import LogEntry, add_log

templates = Jinja2Templates(directory="app/templates")

async def handle(request: Request, path: str):
    host = request.headers.get("host", "").lower().split(":")[0]
    config = load_config()
    routes = config.get("routes", {})
    backend_url = routes.get(host)

    if not backend_url:
        return templates.TemplateResponse("setup.html", {
            "request": request,
            "host": host
        })

    start = time.monotonic()
    try:
        headers = {
            k: v for k, v in request.headers.items()
            if k.lower() not in ("host", "content-length")
        }
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.request(
                method=request.method,
                url=f"{backend_url}/{path}",
                headers=headers,
                params=dict(request.query_params),
                content=await request.body()
            )
        duration = int((time.monotonic() - start) * 1000)
        add_log(LogEntry(
            timestamp=time.time(), domain=host, path=f"/{path}",
            method=request.method, status=resp.status_code,
            backend=backend_url, duration_ms=duration
        ))
        # Strip problematic headers before returning
        excluded = {"content-encoding", "transfer-encoding", "content-length"}
        clean_headers = {k: v for k, v in resp.headers.items() if k.lower() not in excluded}
        return Response(content=resp.content, status_code=resp.status_code, headers=clean_headers)
    except Exception as e:
        duration = int((time.monotonic() - start) * 1000)
        add_log(LogEntry(
            timestamp=time.time(), domain=host, path=f"/{path}",
            method=request.method, status=502,
            backend=backend_url, duration_ms=duration, error=str(e)
        ))
        return HTMLResponse(
            content=f"""<!DOCTYPE html><html><head><title>502 - Proxy Error</title>
            <style>body{{font-family:sans-serif;background:#0a0a0f;color:#e8e8f0;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;}}
            .box{{text-align:center;padding:3rem;background:#16213e;border-radius:16px;border:1px solid #ff5252;}}
            h1{{color:#ff5252;font-size:3rem;margin-bottom:1rem;}} p{{color:#8888aa;}}</style></head>
            <body><div class='box'><h1>502</h1><p>Backend unreachable: <code>{backend_url}</code></p><p>{str(e)}</p></div></body></html>""",
            status_code=502
        )
