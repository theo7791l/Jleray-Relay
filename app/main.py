from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import asyncio

from app.auth import ensure_default_password
from app.config import load_config
from app.routers import admin, proxy
from app.ws_manager import manager
from app.logger import set_broadcast_callback
from app.checker import check_all
from app.health_history import record

app = FastAPI(title="Jleray-Relay", version="1.0.0")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(admin.router, prefix="/admin")

async def health_poll_loop():
    """Poll all backends every 60s and record history."""
    await asyncio.sleep(10)  # wait for startup
    while True:
        try:
            config = load_config()
            routes = config.get("routes", {})
            if routes:
                statuses = await check_all(routes)
                for domain, status in statuses.items():
                    record(domain, status.get("online", False), status.get("latency_ms", 0))
        except Exception as e:
            print(f"Health poll error: {e}")
        await asyncio.sleep(60)

@app.on_event("startup")
async def startup():
    ensure_default_password()
    set_broadcast_callback(manager.broadcast)
    asyncio.create_task(health_poll_loop())
    print("🔀 Jleray-Relay started!")
    print("📍 Admin: http://YOUR_IP:7435/admin/login")

@app.websocket("/ws/logs")
async def ws_logs(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def reverse_proxy(request: Request, path: str):
    return await proxy.handle(request, path)
