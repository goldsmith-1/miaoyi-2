import time

from fastapi import Depends, HTTPException, Request

from .auth import current_user
from .config import settings


async def rate_limit(request: Request, user: dict = Depends(current_user)) -> dict:
    """Fixed-window limiter in Redis: N requests per user per minute."""
    redis = request.app.state.redis
    key = f"rl:{user['sub']}:{int(time.time() // 60)}"
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, 90)
    if count > settings.rate_limit_per_minute:
        raise HTTPException(429, "Too many requests. Please wait a minute and try again.")
    return user
