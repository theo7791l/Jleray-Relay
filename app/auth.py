import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Request, HTTPException
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import load_config, save_config

SECRET_KEY = os.getenv("SECRET_KEY", "changez-moi-en-production-jleray-relay-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = timedelta(hours=24)

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)

def create_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + ACCESS_TOKEN_EXPIRE
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

def get_current_admin(request: Request):
    token = request.cookies.get("relay_token")
    if not token:
        raise HTTPException(status_code=307, headers={"Location": "/admin/login"})
    payload = decode_token(token)
    if not payload or payload.get("sub") != "admin":
        raise HTTPException(status_code=307, headers={"Location": "/admin/login"})
    return payload

def ensure_default_password():
    config = load_config()
    if not config.get("admin_password_hash"):
        config["admin_password_hash"] = hash_password("admin123")
        save_config(config)
        print("⚠️  Mot de passe par défaut activé : admin123 — changez-le dans le panel !")
