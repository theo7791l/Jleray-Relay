# 🔀 Jleray-Relay

> A powerful Python-based reverse proxy with a beautiful animated web UI.

## Features
- 🌐 Route multiple domains to different backends
- 🔐 Secure admin authentication
- 🎨 Beautiful animated web interface
- ⚙️ Fully configurable from the browser
- 💾 JSON-based persistent config

## Installation

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 7435
```

On first launch, connect to `http://YOUR_IP:7435/admin` with password: `admin123`

## Phases
- [x] Phase 1 — Auth + base UI skeleton
- [ ] Phase 2 — Domain management UI (add/remove/edit routes)
- [ ] Phase 3 — Live proxy routing by Host header
- [ ] Phase 4 — Profile page + password change
- [ ] Phase 5 — Dashboard stats, animations, polish
