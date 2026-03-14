# 🔀 Jleray-Relay

> A powerful Python-based reverse proxy with a beautiful animated web UI.

## Features
- 🌐 Route multiple domains to different backends
- 🔐 Secure admin authentication (JWT + bcrypt)
- 🎨 Beautiful animated dark glassmorphism UI
- 📊 Real-time backend status checks (ping + latency)
- 📋 Live request logs with filters (domain, status, method)
- ⚙️ Fully configurable from the browser, no restart needed
- 💾 JSON-based persistent config

## Installation

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 7435
```

On first launch, go to `http://YOUR_IP:7435/admin/login` — password: **`admin123`**

## Routes

| URL | Description |
|---|---|
| `/admin/login` | Login page |
| `/admin/dashboard` | Manage routes + live status |
| `/admin/logs` | Live request logs |
| `/admin/profile` | Change password |
| `/admin/api/status` | JSON: backend status |
| `/admin/api/logs` | JSON: request logs |
| `/admin/api/stats` | JSON: traffic stats |

## How it works

```
User → test1.awlor.online → Jleray-Relay (port 7435)
                                    ↓ (reads Host header)
                            routes["test1.awlor.online"] = "http://12.34.56.78:8080"
                                    ↓
                            Forwards request to http://12.34.56.78:8080
```

## Dev phases
- [x] Phase 1 — Auth + base UI skeleton
- [x] Phase 2 — Live status checks, request logs, JSON API
- [ ] Phase 3 — Toast notifications, animated route cards, WebSocket live logs
- [ ] Phase 4 — Domain health history graph, per-domain stats
- [ ] Phase 5 — Final polish, mobile responsive, dark/light toggle
