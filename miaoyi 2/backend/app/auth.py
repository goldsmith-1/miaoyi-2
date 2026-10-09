"""Verifies Supabase-issued JWTs. The mobile app signs users in with Supabase and sends the access token."""
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import settings

bearer = HTTPBearer(auto_error=False)


def verify_token(token: str, secret: str) -> dict:
    try:
        return jwt.decode(token, secret, algorithms=["HS256"], audience="authenticated")
    except jwt.PyJWTError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token") from exc


async def current_user(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict:
    if creds is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")
    if not settings.supabase_jwt_secret:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Auth is not configured")
    return verify_token(creds.credentials, settings.supabase_jwt_secret)
