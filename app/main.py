from fastapi import FastAPI, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import httpx

from app.auth import ensure_default_password
from app.config import load_config
from app.routers import admin, proxy

app = FastAPI(title="Jleray-Relay", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include admin router
app.include_router(admin.router, prefix="/admin")

@app.on_event("startup")
async def startup():
    ensure_default_password()
    print("🔀 Jleray-Relay started!")
    print("📍 Admin panel: http://YOUR_IP:7435/admin")

# Catch-all proxy route (must be last)
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def reverse_proxy(request: Request, path: str):
    return await proxy.handle(request, path)
