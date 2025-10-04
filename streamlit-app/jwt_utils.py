import jwt
import os
from datetime import datetime, timedelta
import secrets

# ----------------- SECRET KEY -----------------
# Try to load from environment variable; otherwise generate a random one (for dev only)
SECRET_KEY = os.getenv("JWT_SECRET_KEY") or secrets.token_urlsafe(32)

def create_jwt(payload: dict, expires_minutes=120):
    """
    Create a JWT token with a payload and expiry time (default 2 hours).
    """
    exp = datetime.utcnow() + timedelta(minutes=expires_minutes)
    payload.update({"exp": exp})
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def decode_jwt(token: str):
    """
    Decode a JWT token and return the payload.
    Returns None if token is expired or invalid.
    """
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        return None  # token expired
    except jwt.InvalidTokenError:
        return None  # invalid token
