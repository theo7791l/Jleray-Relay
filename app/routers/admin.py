from fastapi import APIRouter, Request, Form, Response, Depends
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.auth import verify_password, create_token, get_current_admin, hash_password
from app.config import load_config, save_config
from app.checker import check_all, check_backend, get_cached_status
from app.logger import get_logs, get_hits, get_total_requests
import asyncio

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# ─── Login ───────────────────────────────────────────────
@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@router.post("/login")
async def login(request: Request, response: Response, password: str = Form(...)):
    config = load_config()
    if verify_password(password, config["admin_password_hash"]):
        token = create_token({"sub": "admin"})
        resp = RedirectResponse(url="/admin/dashboard", status_code=303)
        resp.set_cookie("relay_token", token, httponly=True, max_age=86400)
        return resp
    return templates.TemplateResponse("login.html", {"request": request, "error": "Mot de passe incorrect"})

@router.get("/logout")
async def logout():
    resp = RedirectResponse(url="/admin/login", status_code=303)
    resp.delete_cookie("relay_token")
    return resp

# ─── Dashboard ───────────────────────────────────────────
@router.get("/dashboard")
async def dashboard(request: Request, auth=Depends(get_current_admin)):
    config = load_config()
    routes = config.get("routes", {})
    statuses = await check_all(routes)
    hits = get_hits()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "routes": routes,
        "count": len(routes),
        "statuses": statuses,
        "hits": hits,
        "total_requests": get_total_requests(),
    })

# ─── Add route ───────────────────────────────────────────
@router.post("/routes/add")
async def add_route(
    domain: str = Form(...),
    backend: str = Form(...),
    auth=Depends(get_current_admin)
):
    config = load_config()
    config["routes"][domain.lower().strip()] = backend.strip()
    save_config(config)
    return RedirectResponse(url="/admin/dashboard", status_code=303)

# ─── Delete route ────────────────────────────────────────
@router.post("/routes/delete")
async def delete_route(domain: str = Form(...), auth=Depends(get_current_admin)):
    config = load_config()
    config["routes"].pop(domain, None)
    save_config(config)
    return RedirectResponse(url="/admin/dashboard", status_code=303)

# ─── Profile / change password ───────────────────────────
@router.get("/profile")
async def profile_page(request: Request, auth=Depends(get_current_admin)):
    return templates.TemplateResponse("profile.html", {"request": request, "success": None, "error": None})

@router.post("/profile")
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    auth=Depends(get_current_admin)
):
    config = load_config()
    if not verify_password(current_password, config["admin_password_hash"]):
        return templates.TemplateResponse("profile.html", {"request": request, "error": "Mot de passe actuel incorrect", "success": None})
    if new_password != confirm_password:
        return templates.TemplateResponse("profile.html", {"request": request, "error": "Les mots de passe ne correspondent pas", "success": None})
    if len(new_password) < 6:
        return templates.TemplateResponse("profile.html", {"request": request, "error": "Mot de passe trop court (6 caractères min)", "success": None})
    config["admin_password_hash"] = hash_password(new_password)
    save_config(config)
    return templates.TemplateResponse("profile.html", {"request": request, "success": "Mot de passe changé avec succès !", "error": None})

# ─── Logs page ────────────────────────────────────────────
@router.get("/logs")
async def logs_page(request: Request, auth=Depends(get_current_admin)):
    return templates.TemplateResponse("logs.html", {"request": request})

# ════════════════════════════════════════════════════════
# API JSON (called by frontend JS via fetch)
# ════════════════════════════════════════════════════════

@router.get("/api/status")
async def api_status(auth=Depends(get_current_admin)):
    """Live backend status check for all routes."""
    config = load_config()
    routes = config.get("routes", {})
    statuses = await check_all(routes)
    return JSONResponse({"statuses": statuses, "total": get_total_requests()})

@router.get("/api/status/{domain:path}")
async def api_status_single(domain: str, auth=Depends(get_current_admin)):
    """Check a single backend by domain."""
    config = load_config()
    routes = config.get("routes", {})
    backend = routes.get(domain)
    if not backend:
        return JSONResponse({"error": "Domain not found"}, status_code=404)
    result = await check_backend(backend)
    return JSONResponse(result)

@router.get("/api/logs")
async def api_logs(limit: int = 50, auth=Depends(get_current_admin)):
    """Return last N request logs."""
    return JSONResponse({"logs": get_logs(limit)})

@router.get("/api/stats")
async def api_stats(auth=Depends(get_current_admin)):
    """Return traffic stats per domain."""
    config = load_config()
    return JSONResponse({
        "hits": get_hits(),
        "total": get_total_requests(),
        "routes_count": len(config.get("routes", {}))
    })
