from fastapi import Request
from fastapi.responses import Response, HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx
from app.config import load_config

templates = Jinja2Templates(directory="app/templates")

async def handle(request: Request, path: str):
    host = request.headers.get("host", "").lower().split(":")[0]
    config = load_config()
    routes = config.get("routes", {})
    backend_url = routes.get(host)

    if not backend_url:
        # Not configured: show setup landing page
        return templates.TemplateResponse("setup.html", {
            "request": request,
            "host": host
        })

    # Proxy the request
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
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=dict(resp.headers)
        )
    except Exception as e:
        return HTMLResponse(f"<h1>Proxy Error</h1><p>{str(e)}</p>", status_code=502)
