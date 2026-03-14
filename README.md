# 🔀 Jleray-Relay

> Reverse proxy intelligent avec dashboard admin temps réel, logs live via WebSocket, historique de santé des backends et interface mobile responsive.

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?style=flat-square&logo=fastapi)
![License](https://img.shields.io/badge/License-MIT-purple?style=flat-square)

---

## ✨ Fonctionnalités

- 🔀 **Reverse proxy multi-domaines** — route les requêtes entrantes selon le `Host` header
- 📡 **Logs en temps réel** via WebSocket — chaque requête apparaît instantanément
- 📊 **Stats par domaine** — uptime %, latence moyenne, graphique historique (Chart.js)
- 🟢 **Statut live** des backends avec latence en ms
- 🔔 **Toast notifications** et dialogs de confirmation stylisés
- 📱 **Interface mobile responsive** avec hamburger menu
- 🔐 **Auth JWT** avec cookie httpOnly, changement de mot de passe
- ⚙️ **Configuration JSON** persistante, hot-reload sans restart

---

## 🚀 Démarrage rapide (local)

```bash
# 1. Cloner le repo
git clone https://github.com/theo7791l/Jleray-Relay.git
cd Jleray-Relay

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer
uvicorn app.main:app --host 0.0.0.0 --port 7435 --reload
```

Ouvrir **http://localhost:7435/admin/login**

Mot de passe par défaut : `admin123` (changez-le immédiatement !)

---

## 🦚 Déploiement sur Pterodactyl

### Prérequis
- Pterodactyl Panel avec accès admin
- Egg Python (voir ci-dessous)
- Port **7435** ouvert sur l’allocation

### Étape 1 — Importer l’Egg

1. Panel Pterodactyl → **Admin → Nests → Import Egg**
2. Importer le fichier `pterodactyl-egg.json` fourni dans ce repo
3. L’egg configure automatiquement :
   - Image Docker : `ghcr.io/parkervcp/yolks:python_3.11`
   - Startup : `uvicorn app.main:app --host 0.0.0.0 --port {{SERVER_PORT}}`
   - Variable `SERVER_PORT` (défaut : 7435)

### Étape 2 — Créer le serveur

1. **Admin → Servers → Create New**
2. Choisir l’egg **Jleray-Relay**
3. Allocation : assigner le port **7435** (ou un port libre)
4. Resources suggérées : 512 MB RAM, 1 CPU, 1 GB disk

### Étape 3 — Upload des fichiers

Option A — via SFTP :
```bash
# Connexion SFTP (crédentiels dans l’onglet Settings du serveur)
sftp user@your-node-ip
put -r . /
```

Option B — via Git (dans la console Pterodactyl) :
```bash
git clone https://github.com/theo7791l/Jleray-Relay.git .
pip install -r requirements.txt
```

### Étape 4 — Lancer

Cliquer sur **Start** dans le panel.
Le serveur est accessible sur `http://VOTRE_IP:7435/admin/login`

### Étape 5 — Domaines (recommandé)

Pour accéder via `relay.awlor.online` au lieu de l’IP :

**Avec Nginx comme reverse proxy devant Jleray-Relay :**
```nginx
server {
    listen 80;
    server_name relay.awlor.online;

    location / {
        proxy_pass http://127.0.0.1:7435;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Puis Certbot pour HTTPS :
```bash
certbot --nginx -d relay.awlor.online
```

---

## 📁 Structure du projet

```
Jleray-Relay/
├── app/
│   ├── main.py              # FastAPI app + WebSocket + health loop
│   ├── auth.py              # JWT + bcrypt
│   ├── config.py            # Lecture/écriture config JSON
│   ├── checker.py           # Ping async backends (latence ms)
│   ├── logger.py            # Ring buffer logs + broadcast WS
│   ├── health_history.py    # Historique uptime par domaine
│   ├── ws_manager.py        # Gestionnaire connexions WebSocket
│   ├── routers/
│   │   ├── admin.py         # Routes admin + API JSON
│   │   └── proxy.py         # Logic reverse proxy
│   ├── templates/           # HTML Jinja2
│   └── static/
│       └── relay.js         # Toast + confirm dialog global
├── data/
│   └── config.json          # Routes + hash mot de passe
├── requirements.txt
├── pterodactyl-egg.json
└── .env.example
```

---

## 🔒 Sécurité

- Mot de passe haché avec **bcrypt** (jamais en clair)
- Auth via **JWT** stocké en cookie `httpOnly` (inaccessible au JS)
- Token expiration : **24h**
- Toutes les routes `/admin/*` protégées par `Depends(get_current_admin)`
- **Changez le mot de passe** dès le premier lancement !

---

## 🛠️ API JSON

| Endpoint | Description |
|---|---|
| `GET /admin/api/status` | Statuts de tous les backends |
| `GET /admin/api/status/{domain}` | Statut d’un seul domaine |
| `GET /admin/api/logs?limit=50` | Derniers N logs |
| `GET /admin/api/stats` | Stats globales + hits |
| `GET /admin/api/history/{domain}` | Historique santé domaine |
| `WS /ws/logs` | WebSocket — stream live des logs |

---

Made with ❤️ by [theo7791l](https://github.com/theo7791l)
