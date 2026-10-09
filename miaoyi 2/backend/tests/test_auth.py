import time

import jwt
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.auth import verify_token
from app.main import app

SECRET = "test-secret-with-enough-length-1234567890"


def token(**over):
    claims = {"sub": "user-1", "aud": "authenticated", "exp": int(time.time()) + 60, **over}
    return jwt.encode(claims, SECRET, algorithm="HS256")


def test_valid_token():
    assert verify_token(token(), SECRET)["sub"] == "user-1"


def test_expired_token_rejected():
    with pytest.raises(HTTPException) as e:
        verify_token(token(exp=int(time.time()) - 10), SECRET)
    assert e.value.status_code == 401


def test_wrong_secret_rejected():
    with pytest.raises(HTTPException):
        verify_token(token(), "another-secret-that-is-long-enough-123456")


def test_health_and_protected_route():
    client = TestClient(app)
    assert client.get("/health").json() == {"status": "ok"}
    assert client.post("/v1/chat", json={"message": "hi"}).status_code == 401
