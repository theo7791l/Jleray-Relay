from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.auth import ensure_default_password
from app.config import load_config
from app.routers import admin, proxy
from app.ws_manager import manager
from app.logger import set_broadcast_callback

app = FastAPI(title="Jleray-Relay", version="1.0.0")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(admin.router, prefix="/admin")

@app.on_event("startup")
async def startup():
    ensure_default_password()
    set_broadcast_callback(manager.broadcast)
    print("🔀 Jleray-Relay started!")
    print("📍 Admin panel: http://YOUR_IP:7435/admin/login")

# WebSocket endpoint for live logs
@app.websocket("/ws/logs")
async def ws_logs(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # keep alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Catch-all proxy (must be last)
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def reverse_proxy(request: Request, path: str):
    return await proxy.handle(request, path)
