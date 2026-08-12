"""
Handles two things:
1. Password hashing — we NEVER store plain-text passwords, only a
   one-way hash. bcrypt is the standard for this.
2. JWT (JSON Web Token) — after login, instead of the server
   remembering "this browser is logged in" in memory, we hand the
   browser a signed token. The browser sends it back on every request
   (as a cookie), and we verify the signature to know it's genuine
   and hasn't been tampered with — without needing a server-side
   session store.
"""

import os
from datetime import datetime, timedelta, timezone

from fastapi import Request, HTTPException, status
from jose import jwt, JWTError
from passlib.context import CryptContext

SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 12  # stay logged in for 12 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def get_current_admin(request: Request) -> str:
    """
    FastAPI dependency used on every protected /admin route.
    Reads the 'admin_token' cookie, verifies it, and returns the
    username if valid. If missing or invalid, redirects to login
    instead of showing a raw 401 error page.
    """
    token = request.cookies.get("admin_token")
    payload = decode_access_token(token) if token else None
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/admin/login"},
        )
    return payload.get("sub")
