import json
import os
from pathlib import Path

CONFIG_FILE = Path("data/config.json")

DEFAULT_CONFIG = {
    "admin_password_hash": "",  # Will be set on first run
    "routes": {}  # domain -> backend_url
}

def load_config() -> dict:
    if not CONFIG_FILE.exists():
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config: dict):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
